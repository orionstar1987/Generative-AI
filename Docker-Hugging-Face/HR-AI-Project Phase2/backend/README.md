cd backend && zip -r ../build.zip ./* -x "venv/*"

az webapp deploy --resource-group test-app-level --name test-app-level-api --type zip --src-path build.zip --async true --timeout 600000 --verbose

colima start

az acr login --name testapplevelacr

docker build -t flask-backend:latest .

docker tag flask-backend:latest testapplevelacr.azurecr.io/flask-backend:latest

docker push testapplevelacr.azurecr.io/flask-backend:latest



RESOURCE_GROUP="ACI"
ACI_NAME="wc-deploy-resources"
IMAGE="testapplevelacr.azurecr.io/wc-deploy:latest"
LOCATION="eastus"
CPU="2"
MEMORY="4"
VNET_NAME="YourVNetName"
SUBNET_NAME="YourSubnetName"



az container create \
  --resource-group ACI \
  --name wc-deploy-resources \
  --image testapplevelacr.azurecr.io/wc-deploy:latest \
  --cpu 2 \
  --memory 4 \
  --location eastus \
  --dns-name-label wc-deploy-resources-dns \
  --ports 80 \
  --restart-policy OnFailure \
  --assign-identity

  --registry-login-server testapplevelacr.azurecr.io \
  --subnet /subscriptions/05a0e0d6-ef38-4407-99ed-957ca2497541/resourceGroups/WCH-E-S-RGP-NET-HRAI-01/providers/Microsoft.Network/virtualNetworks/WCH-E-S-VNT-HRAI-01/subnets/ACI \