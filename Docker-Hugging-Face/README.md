## [Build Generative AI Apps with Docker And Hugging Face's Docker Spaces](https://www.youtube.com/watch?v=aA76uj5kQac)

## Steps

- Create requirements.txt

- Create app.py

- Create Dockerfile

- Create Huggingface Space https://huggingface.co/orionstar1987
    - Use 'mit' license
    - Choose 'Blank' Docker SDK

- In the space created, go to Files > Add File > Upload Files. Drag the 3 files into Upload file(s) section. Commit changes

- Since in the Docker file, all execution steps have been specified, once the files are uploaded, it will automatically run
    - Check from the "App" tab (Build, Container)
    - This message below indicates the app has started successfully

```bash
===== Application Startup at 2024-07-22 18:06:16 =====

INFO:     Started server process [1]

INFO:     Waiting for application startup.

INFO:     Application startup complete.

INFO:     Uvicorn running on http://0.0.0.0:7860 (Press CTRL+C to quit)

```

- In the space, there are "3 dots" on the uppper-right conner next to "Settings". Choose "Embed this Space". Click the URL under "Direct URL", like https://orionstar1987-text2textwithdockers.hf.space

- Add "/docs" at the end of the URL, like https://orionstar1987-text2textwithdockers.hf.space/docs. This will start a Swagger UI for the FASTAPI
    - Under /generate, we can test what the "text2text-generation" model can output, given our input


