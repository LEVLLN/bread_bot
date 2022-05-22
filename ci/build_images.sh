docker build -f ci/Dockerfile -t levkey/bread_bot:base .
docker build -f ci/Dockerfile.app -t levkey/bread_bot:app .
