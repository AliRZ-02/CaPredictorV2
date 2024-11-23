# CaPredictorV2
Free Hockey Visualizations & Market Valuations. Built with MERN + Python + AWS (Lambda) Stack.

## Link
- [CaPredictorV2](https://www.capredictor.com/)

## Stack

- [Backend](https://github.com/AliRZ-02/CaPredictorV2Backend)
  - Mongo
  - Node
  - Express
  - TypeScript
- [Frontend](https://github.com/AliRZ-02/CaPredictorV2Frontend)
  - Node
  - React
  - MaterialUI
  - TypeScript
- [Model API](https://github.com/AliRZ-02/CaPredictorV2Models)
  - Python
  - FastAPI
  - Scikit-Learn (Linear Regression)
- [Data Population Script](https://github.com/AliRZ-02/CaPredictorV2)
  - Python
  - Mongo
 
 
### To deploy on AWS

- Ensure AWS credentials are stored in a .env file, `AWS_ACCESS_KEY` and `AWS_ACCESS_SECRET`
- Install AWS `sam`
- `sam build`
- `sam local invoke '<FunctionName>` to test locally
- `sam deploy --guided` to deploy to AWS
