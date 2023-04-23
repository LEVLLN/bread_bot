# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/LEVLLN/bread_bot/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                                   |    Stmts |     Miss |     Cover |   Missing |
|--------------------------------------------------------------------------------------- | -------: | -------: | --------: | --------: |
| bread\_bot/auth/methods/auth\_methods.py                                               |       54 |        2 |     96.3% |   81, 109 |
| bread\_bot/auth/models/users.py                                                        |       14 |        1 |     92.9% |        18 |
| bread\_bot/auth/routes/auth.py                                                         |       32 |        4 |     87.5% | 41, 66-68 |
| bread\_bot/auth/schemas/auth.py                                                        |       22 |        0 |    100.0% |           |
| bread\_bot/common/clients/baneks\_client.py                                            |       25 |       10 |     60.0% |20, 23-30, 33-47 |
| bread\_bot/common/clients/evil\_insult\_client.py                                      |        8 |        2 |     75.0% |     10-18 |
| bread\_bot/common/clients/forismatic\_client.py                                        |        8 |        2 |     75.0% |     10-13 |
| bread\_bot/common/clients/great\_advice.py                                             |       10 |        2 |     80.0% |     14-18 |
| bread\_bot/common/clients/telegram\_client.py                                          |       62 |       30 |     51.6% |41-48, 56-69, 77-85, 88-97, 100-101, 112, 116 |
| bread\_bot/common/exceptions/base.py                                                   |        6 |        0 |    100.0% |           |
| bread\_bot/common/exceptions/commands.py                                               |        5 |        0 |    100.0% |           |
| bread\_bot/common/models/answer\_entities.py                                           |       19 |        0 |    100.0% |           |
| bread\_bot/common/models/answer\_packs.py                                              |       24 |        0 |    100.0% |           |
| bread\_bot/common/models/answer\_packs\_to\_chats.py                                   |       11 |        0 |    100.0% |           |
| bread\_bot/common/models/chats.py                                                      |       12 |        0 |    100.0% |           |
| bread\_bot/common/models/chats\_to\_members.py                                         |       11 |        0 |    100.0% |           |
| bread\_bot/common/models/dictionary\_entity.py                                         |        8 |        0 |    100.0% |           |
| bread\_bot/common/models/members.py                                                    |       11 |        0 |    100.0% |           |
| bread\_bot/common/routes/common.py                                                     |       50 |       22 |     56.0% |32-34, 41-49, 54, 65-68, 73-83 |
| bread\_bot/common/schemas/api\_models.py                                               |       30 |        0 |    100.0% |           |
| bread\_bot/common/schemas/bread\_bot\_answers.py                                       |       22 |        1 |     95.5% |        11 |
| bread\_bot/common/schemas/commands.py                                                  |       28 |        0 |    100.0% |           |
| bread\_bot/common/schemas/telegram\_messages.py                                        |       56 |        0 |    100.0% |           |
| bread\_bot/common/services/commands/command\_parser.py                                 |      114 |       12 |     89.5% |64-65, 107-108, 159-163, 200, 206-207 |
| bread\_bot/common/services/commands/command\_settings.py                               |       28 |        0 |    100.0% |           |
| bread\_bot/common/services/handlers/answer\_handler.py                                 |      108 |       15 |     86.1% |55-56, 59, 85, 87, 92-97, 129, 134, 150, 174 |
| bread\_bot/common/services/handlers/command\_handler.py                                |       28 |        9 |     67.9% | 23, 35-42 |
| bread\_bot/common/services/handlers/command\_methods/admin\_command\_method.py         |      118 |       13 |     89.0% |40, 46, 55-56, 59, 96, 107, 145, 149, 167-168, 192, 213 |
| bread\_bot/common/services/handlers/command\_methods/base\_command\_method.py          |       55 |       25 |     54.5% |     74-99 |
| bread\_bot/common/services/handlers/command\_methods/entertainment\_command\_method.py |      155 |       72 |     53.5% |39-52, 93-106, 109-127, 130-143, 146-149, 152-155, 158-161, 164-172, 184 |
| bread\_bot/common/services/handlers/command\_methods/integration\_command\_method.py   |       41 |        2 |     95.1% |     21-22 |
| bread\_bot/common/services/handlers/command\_methods/member\_command\_method.py        |       68 |        4 |     94.1% |47-48, 80, 83 |
| bread\_bot/common/services/handlers/handler.py                                         |       36 |        1 |     97.2% |        26 |
| bread\_bot/common/services/member\_service.py                                          |       98 |       12 |     87.8% |32, 53-54, 56-62, 75-76, 156, 158, 160 |
| bread\_bot/common/services/messages/message\_receiver.py                               |       44 |        2 |     95.5% |    40, 51 |
| bread\_bot/common/services/messages/message\_sender.py                                 |       57 |       29 |     49.1% |33-45, 63, 79-102 |
| bread\_bot/common/services/messages/message\_service.py                                |       47 |        9 |     80.9% |51-53, 55-56, 60-64 |
| bread\_bot/common/services/morph\_service.py                                           |       90 |        3 |     96.7% |42, 64, 98 |
| bread\_bot/common/utils/functions.py                                                   |        4 |        0 |    100.0% |           |
| bread\_bot/common/utils/structs.py                                                     |       65 |        0 |    100.0% |           |
| bread\_bot/main/base\_client.py                                                        |       46 |        2 |     95.7% |     92-93 |
| bread\_bot/main/database/base.py                                                       |       12 |        0 |    100.0% |           |
| bread\_bot/main/database/mixins.py                                                     |      143 |       13 |     90.9% |39, 64-66, 120-122, 229-231, 256, 260, 285 |
| bread\_bot/main/routes.py                                                              |        9 |        0 |    100.0% |           |
| bread\_bot/main/settings/default.py                                                    |       30 |        0 |    100.0% |           |
| bread\_bot/main/webserver.py                                                           |       20 |        0 |    100.0% |           |
| bread\_bot/utils/dependencies.py                                                       |       17 |        8 |     52.9% |21-25, 32-36 |
| bread\_bot/utils/helpers.py                                                            |       18 |        1 |     94.4% |        40 |
| bread\_bot/utils/json\_logger.py                                                       |       41 |        3 |     92.7% |46, 89, 95 |
| bread\_bot/utils/middlewares.py                                                        |      122 |       11 |     91.0% |80, 103-104, 203, 214-216, 239-240, 248-249 |
| bread\_bot/utils/testing\_tools.py                                                     |       35 |        4 |     88.6% |     35-39 |
| bread\_bot/utils/utils\_schemas.py                                                     |       38 |        0 |    100.0% |           |
|                                                                              **TOTAL** | **2215** |  **326** | **85.3%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/LEVLLN/bread_bot/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/LEVLLN/bread_bot/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/LEVLLN/bread_bot/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/LEVLLN/bread_bot/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2FLEVLLN%2Fbread_bot%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/LEVLLN/bread_bot/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.