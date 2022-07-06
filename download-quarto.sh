wget https://quarto.org/docs/download/_download.json 
ver=$(grep -o '"version": "[^"]*' _download.json | grep -o '[^"]*$')
wget https://github.com/quarto-dev/quarto-cli/releases/download/v${ver}/quarto-${ver}-linux-amd64.deb
sudo dpkg -i quarto-${ver}-linux-amd64.deb
rm quarto-${ver}-linux-amd64.deb
rm _download.json
