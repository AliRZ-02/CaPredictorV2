# To deploy on AWS

- Ensure AWS credentials are stored in a .env file, `AWS_ACCESS_KEY` and `AWS_ACCESS_SECRET`
- Install AWS `sam`
- `sam build`
- `sam local invoke '<FunctionName>` to test locally
- `sam deploy --guided` to deploy to AWS