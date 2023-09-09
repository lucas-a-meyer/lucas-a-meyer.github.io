import argparse
import logging
import os
import time
from datetime import datetime
from typing import Tuple

import semantic_kernel as sk
import yaml
from dotenv import load_dotenv
from semantic_kernel.planning.basic_planner import BasicPlanner

from blogmaster.kernel import initialize_kernel
from quarto_blog_utils.blog_images import upload_image_to_azure_storage
from quarto_blog_utils.headers import check_header, update_header_dates
from quarto_blog_utils.posts import generate_slug_from_title
from quarto_blog_utils.quarto import upgrade_quarto


def openai_call(func):
    def wrapper_func(*args, **kwargs):
        logger.info('Calling something that depends on OpenAI')
        max_attempts = 5
        attempts = 0
        while attempts < max_attempts:
            try:        
                logger.info(f'Attempt {attempts+1} of {max_attempts} of reviewing post grammar')                  
                result = func(*args, **kwargs)
                logger.info('Sleeping 60')
                time.sleep(60)
                break
            except:
                attempts += 1
                logger.info(f'Attempt {attempts} failed. Retrying.')
                time.sleep(60)
        return result
    return wrapper_func

@openai_call
def review_post_grammar(kernel: sk.Kernel, article_body) -> str:
    return str(kernel.review_post(article_body))


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]",
        description="Processes blog posts and generates a static website.",
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version = f"{parser.prog} version {GLOBAL_VERSION}"
    )
    parser.add_argument('--start_date', dest='start_date', type=str, help='Start date in YYYY-MM-DD format', default="1900-01-01", required=False)
    parser.add_argument('--end_date', dest='end_date', type=str, help='End date in YYYY-MM-DD format', default="3000-12-31", required=False)
    
    parser.add_argument('-u', '--update_quarto', dest='update_quarto', help='Update quarto to the latest version', action="store_true")
    return parser


def check_headers(start_date: str, end_date: str) -> None:
    """
    Check the headers of all posts between start_date and end_date.
    Parameters:
        start_date (str): The start date in YYYY-MM-DD format
        end_date (str): The end date in YYYY-MM-DD format
    """

    logger.info(f'Started checking headers at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    # List all files in the posts directory between start_date and end_date
    # For each file, print the name of the file and the date in the file
    for fname in os.listdir('posts'):
        logger.info(f'Started processing {fname} at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

        if fname.endswith('.qmd'):
            # get the first 10 characters of fname, which will be the post date
            post_date = fname[:10]
            if post_date >= start_date and post_date <= end_date:

                # split the file into header and body
                with open(f'posts/{fname}', 'r', encoding='utf-8') as f:
                    file_contents = f.read()
                    article_yaml_header = file_contents.split('---')[1]
                    # article_body = file_contents.split('---')[2]

                    # print(f"Article YAML header: {article_yaml_header}")
                    if check_header(article_yaml_header):
                        logger.info(f"Header is valid")
                    else:
                        logger.error(f"Header is invalid")

                time.sleep(0.1)
            else:
                logger.info("Skipping file {fname} because it's not in the date range")
        else:
            logger.info("Skipping file {fname} because it's not a .qmd file")

    logger.info(f'Finished checking headers at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')


def parse_args() -> Tuple[bool, str, str]:

    argp = init_argparse()
    args = argp.parse_args()

    update_quarto = args.update_quarto
    start_date = args.start_date
    end_date = args.end_date

    if start_date > end_date:
        logger.error('Start date must be before end date')
        exit(1)

    # check if start_date and end_date are valid dates
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        logger.error('Invalid date format. Use YYYY-MM-DD')
        exit(1)

    return update_quarto, start_date, end_date


def process_staged_posts(kernel: sk.Kernel) -> None:
    """
    Process the staged posts in the staged_posts folder and generate the final posts
    Parameters:
        kernel: The semantic kernel to use for generating the final posts
    """

    # iterate over the .qmd files in the staged_posts folder
    logger.info('Processing staged posts started')

    for fname in os.listdir('staged_posts'):
        # check that it's a file, not a directory
        if not os.path.isfile(f'staged_posts/{fname}'):
            logger.info(f'{fname} is not a file. Skipping.')
            continue

        # check that the extension is .qmd
        if not fname.endswith('.qmd'):
            logger.info(f'{fname} is not a .qmd file. Skipping.')
            continue
        
        # read the file contents
        with open(f'staged_posts/{fname}', 'r', encoding='utf-8') as f:
            logger.info(f'Started processing staged post from file {fname}')

            # get the yaml header and the post content
            file_contents = f.read()

        # Split the file contents into the yaml header and the post content
        article_yaml_header = file_contents.split('---')[1]
        dict_header = yaml.load(article_yaml_header, Loader=yaml.FullLoader)
        article_body = file_contents.split('---')[2]

        # If the article is a draft, skip it
        if dict_header['draft']:
            logger.info(f'{fname} is a draft. Skipping.')
            continue

        # Copy the file to the staged_posts_processed folder
        logger.info(f'Copying {fname} to staged_posts_processed folder')
        with open(f'staged_posts/processed/{fname}', 'w', encoding='utf-8') as f:
            f.write(file_contents)

        # get the image file location from dict_header
        image_file_location = dict_header['image']

        # convert relative path to full path
        image_file_location = os.path.abspath(image_file_location)

        # upload the image to azure storage
        image_url = upload_image_to_azure_storage(image_file_location)
        logger.info(f'Image uploaded to {image_url}')

        # Update the dict_header with the image url
        dict_header['image'] = image_url

        # generate the slug from the title
        slug = generate_slug_from_title(dict_header['title'])

        # Generate the file name with the date in the format YYYY-MM-DD and the slug
        file_name = f'{dict_header["date"].strftime("%Y-%m-%d")}-{slug}.qmd'

        dict_header = update_header_dates(dict_header)

        # change the field reset to true
        dict_header['reset'] = True

        # Review grammar      
        article_body = review_post_grammar(kernel, article_body)

        # generate the final post by writing the yaml header and the post content to a file in the posts directory
        logger.info(f'Writing final post to posts directory: {file_name}')
        with open(f'posts/{file_name}', 'w', encoding='utf-8') as f:
            f.write('---\n')
            yaml.dump(dict_header, f)
            f.write('---\n')
            f.write(article_body)
            f.write('\n')
        
        # delete the file from the staged_posts folder
        logger.info(f'Deleting {fname} from staged_posts folder')
        os.remove(f'staged_posts/{fname}')

        logger.info(f'Processing staged post from file {fname} completed')

    logger.info('Processing staged posts completed')


def process_ideas(kernel: sk.Kernel) -> None:
    """
    Process the ideas in the ideas folder and generate skeleton posts
    Parameters:
        kernel: The semantic kernel to use for generating the skeleton posts
    """

    logger.info('Processing ideas started')
    
    # Iterate over the files in the ideas folder
    for fname in os.listdir('ideas'):
        
        # check that it's a file, not a directory
        if not os.path.isfile(f'ideas/{fname}'):
            logger.info(f'{fname} is not a file. Skipping.')
            continue

        #  open the file and read its contents
        with open(f'ideas/{fname}', 'r', encoding='utf-8') as f:
            logger.info(f'Started processing idea from file {fname}')

            # read the idea into a variable
            idea = f.read()
           
        logger.info(f'Generating skeleton post from idea {fname}')
        post_skeleton = str((openai_call(kernel.generate_skeleton(idea))))
        logger.info(f'Skeleton post generated from idea {fname}')

        logger.info(f'Generating content from skeleton {fname}')
        post_content = str((openai_call(kernel.generate_post(post_skeleton))))
        logger.info(f'Generating content from skeleton {fname}')

        # write the skeleton post to the staging folder
        with open(f'staged_posts/suggestions/{fname}', 'w', encoding='utf-8') as f:
            f.write(post_content)
            logger.info(f'Post content written to staged_posts/suggestions folder {fname}')

        # move the file to the ideas processed folder
        os.rename(f'ideas/{fname}', f'ideas/ideas_processed/{fname}')    
        logger.info(f'Finished processing idea from file {fname}')
    
    logger.info('Processing ideas completed')


def main() -> None:
    # Initialize the logger
    logger.info(f'BlogMaster version {GLOBAL_VERSION} started')
       
    update_quarto, start_date, end_date = parse_args()
    logger.info('Arguments received:')
    logger.info(f'\tupdate_quarto: {update_quarto}')
    logger.info(f'\tstart_date: {start_date}')
    logger.info(f'\tend_date: {end_date}')
    
    # If the user wants to update quarto, let's do that and exit
    if update_quarto:
        logger.info('Updating Quarto')
        upgrade_quarto()
        exit(0)

    ## If the user doesn't want to update Quarto, let's do everything we can to update the blog
    kernel = initialize_kernel()
    kernel.set_default_text_completion_service("gpt4")

    # process_ideas looks into the /ideas folder and generates skeleton posts
    # The generated posts are saved in the /staged_posts/suggestions folder
    process_ideas(kernel)

    # process_staged_posts looks into the /staged_posts folder and generates final posts
    process_staged_posts(kernel)

    logger.info(f'Processing blog completed')
    exit(0)

if __name__ == '__main__':

    GLOBAL_VERSION = "2023-05-20"
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("blogmaster")

    logger_blocklist = [
        "azure.core.pipeline.policies.http_logging_policy",
    ]

    for module in logger_blocklist:
        logging.getLogger(module).setLevel(logging.WARNING)

    load_dotenv("~/.env")
    main()

