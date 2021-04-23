NAME=tasc-lambda
CREATE_LAMBDA=false
while getopts cn: flag
do
    case "${flag}" in
        c) CREATE_LAMBDA=true;;
        n) NAME=${OPTARG};;
    esac
done
zip -r $NAME.zip .
aws s3 cp $NAME.zip s3://tasc-lambdas
if [[ CREATE_LAMBDA ]]
    then aws lambda create-function --function-name $NAME --runtime python3.7 --role arn:aws:iam::861473675836:role/TASCLambda --handler lambda_function.lambda_handler --timeout 120 --memory-size 2048 --code "{'S3Bucket':'tasc-lambdas','S3Key':'${NAME}.zip'}"
else
    aws lambda update-function-code --s3-bucket "tasc-lambdas" --s3-key "${NAME}.zip" --function-name $NAME
fi 
