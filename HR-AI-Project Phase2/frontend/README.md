# Build and Deployment

Before doing the deployment described below azure CLI should be authorized and a correct subscription should be set
```bash
azure cli login
```
```bash
az account set --subscription <subscription-id>
```

---

To build and deploy the frontend side from the local machine the following steps should be done

1. In the frontend folder install all npm dependencies
```bash
npm install && npm install --prefix ./server
```

2. Run build for dev or production
```bash
npm run build:prod
```

3. Create a zip of the build files
```bash
cd server && zip -r ../build.zip ./*
```

4. Deploy zip file to web app via azure CLI
```bash
az webapp deploy --resource-group test-app-level --name test-app-level-ui --src-path build.zip
```

For now the following resource group and web app can be used
```bash
resource-group = test-app-level
test-app-level-ui = test-app-level-ui
```