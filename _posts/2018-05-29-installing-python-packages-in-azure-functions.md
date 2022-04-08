---
title: Tricks using Python in Azure Functions
author: Lucas A. Meyer
date: '2018-05-29'
categories:
  - Data Science
  - Python
---


If you don't know anything about Azure Functions, [this](https://docs.microsoft.com/en-us/azure/azure-functions/) is a good place to start.

> Azure Functions is a serverless compute service that enables you to run code on-demand without having to explicitly provision or manage infrastructure. Use Azure Functions to run a script or piece of code in response to a variety of events. Learn how to use Azure Functions with our quickstarts, tutorials, and samples.

Here are some tricks to use Azure Functions with Python, which is currently (May 2018) under "experimental" support. Azure Functions, being serverless, are inexpensive but still very useful. I have used Azure Functions to create APIs for my data science projects (e.g., trigger a retraining, evaluate a submission online) and to create a Twitter Bot that posts a few random pictures every day. The major limitation of Azure Functions is that the free version will only run for 10-15 minutes.


#### Installing a more recent version of Python for your Azure Functions

The default Python version in Azure Functions is pretty old. As of this writing (May 2018), it's still on version 2.7. You can install newer versions of Python using the procedure below. This procedure installs Python 3.5.

1. Open the [Azure Portal](https://portal.azure.com)

2. Select your function App (usually under App Services)

3. Select "Platform Features" on top
    ![Platform Features](/img/python-platform.png)

4. Select "Advanced Tools (Kudu)"

    ![Select Kudu](/img/python-kudu1.png)

5. Select "CMD" on the "Debug Console"

    ![Debug Console -> CMD](/img/python-kudu.png)

    Now the fun part starts. Thanks to [Our Way of Lyf](https://ourwayoflyf.com/running-python-code-on-azure-functions-app/) for providing instructions.

6. We first download and install Python using Nuget. To see all possible versions, please check the following website: [https://www.siteextensions.net/profiles/steve.dower](https://www.siteextensions.net/profiles/steve.dower)

    ```bash
    nuget.exe install -Source https://www.siteextensions.net/api/v2/ -OutputDirectory D:\home\site\tools python352x64 
    ```

    For me, this step took approximately 4 minutes.
    
    > Successfully installed 'python352x64 3.5.2.6' to D:\home\site\tools
    
    > Executing nuget actions took 3.99 min

7. We now move Python to its proper place:

    ```bash
    mv /d/home/site/tools/python352x64.3.5.2.6/content/python35/* /d/home/site/tools/
    ```

From now on, whatever function we write using Python in this app will use the new version. To verify, let's create a function using Python and check its version. Remember that in order to create Azure Functions using Python, we first have to enable "Experimental Language Support"). For this test, I'll create a function with an HTTP trigger, which I'll later change to a Timer trigger.

![create new function](/img/python-new-function.png)


```python
import os
import platform

message = "Using Python version {0}".format(platform.python_version())
print(message)
```

> 2018-05-30T01:34:29.954 [Info] Function started (Id=c7edfee9-b370-4dfb-bf89-2912cd09a109)
>
> 2018-05-30T01:34:35.923 [Info] Using Python version 3.5.2
>
> 2018-05-30T01:34:35.955 [Info] Function completed (Success, Id=c7edfee9-b370-4dfb-bf89-2912cd09a109, Duration=6011ms)
>

#### Installing packages

Now that we have a recent version of Python, we can install whatever packages we want. For example, we can install pyodbc and python-twitter.

```bash
D:\home\site\tools\python.exe -m pip install pyodbc
D:\home\site\tools\python.exe -m pip install python-twitter
```

With these packages installed, for example, I can connect to a SQL (or SQL Azure) database and write a Python script that tweets parts of its content.

#### Converting an HTTP Trigger to a time trigger

By default, Python functions don't have a timer trigger. But that's no big deal. Start with an HTTP trigger (see picture above), and then go to "Integrate" and delete the trigger.

![Delete trigger](/img/python-delete-trigger.png)

Once you delete the trigger, you'll be able to add a new trigger, which can be a Timer trigger.

![Timer trigger](/img/python-new-trigger.png)

You can configure the trigger using the usual `cron` syntax:

![Configuring timer trigger](/img/python-timer-trigger.png)

In the example above, I'm triggering the function every 15 seconds. I did not change the code from before, so this will result simply in Python printing its version to the log every 15 seconds.

![Configuring timer trigger](/img/python-timer-trigger-results.png)

#### A few ideas on how to use this

If you know Python and have an Azure subscription, here's a few things that you do for free or nearly for free with this. You can:

* trigger a Python function that wakes up every day and performs some database maintentance (e.g., triggers a stored procedure that deletes old records)

* send a message in Twitter every day, for example "Since yesterday, we've acquired X followers"

* Read new data from a database, run a model that creates a forecast and save it back to the database every 2 hours

Serverless computing is extremely convenient: although there are limitations on what the free tier can do, they're not too restrictive.


