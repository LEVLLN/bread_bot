# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/LEVLLN/bread_bot/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                                   |    Stmts |     Miss |     Cover |   Missing |
|--------------------------------------------------------------------------------------- | -------: | -------: | --------: | --------: |
| bread\_bot/auth/methods/auth\_methods.py                                               |       54 |        2 |     96.3% |   81, 109 |
| bread\_bot/auth/models/users.py                                                        |       14 |        1 |     92.9% |        18 |
| bread\_bot/auth/routes/auth.py                                                         |       32 |        4 |     87.5% | 41, 66-68 |
| bread\_bot/auth/schemas/auth.py                                                        |       22 |        0 |    100.0% |           |
| bread\_bot/common/async\_tasks.py                                                      |       18 |        0 |    100.0% |           |
| bread\_bot/common/clients/baneks\_client.py                                            |       25 |       10 |     60.0% |20, 23-30, 33-47 |
| bread\_bot/common/clients/evil\_insult\_client.py                                      |        8 |        2 |     75.0% |     10-18 |
| bread\_bot/common/clients/forismatic\_client.py                                        |        8 |        2 |     75.0% |     10-13 |
| bread\_bot/common/clients/great\_advice.py                                             |       10 |        2 |     80.0% |     14-18 |
| bread\_bot/common/clients/openai\_client.py                                            |       48 |        8 |     83.3% |39, 59, 62-68 |
| bread\_bot/common/clients/telegram\_client.py                                          |       62 |       30 |     51.6% |41-48, 56-69, 77-85, 88-97, 100-101, 112, 116 |
| bread\_bot/common/exceptions/base.py                                                   |        6 |        0 |    100.0% |           |
| bread\_bot/common/exceptions/commands.py                                               |        5 |        0 |    100.0% |           |
| bread\_bot/common/models/answer\_entities.py                                           |       20 |        0 |    100.0% |           |
| bread\_bot/common/models/answer\_packs.py                                              |       24 |        0 |    100.0% |           |
| bread\_bot/common/models/answer\_packs\_to\_chats.py                                   |       11 |        0 |    100.0% |           |
| bread\_bot/common/models/chats.py                                                      |       14 |        0 |    100.0% |           |
| bread\_bot/common/models/chats\_to\_members.py                                         |       11 |        0 |    100.0% |           |
| bread\_bot/common/models/dictionary\_entity.py                                         |        8 |        0 |    100.0% |           |
| bread\_bot/common/models/members.py                                                    |       11 |        0 |    100.0% |           |
| bread\_bot/common/routes/common.py                                                     |       47 |       20 |     57.4% |32, 37-45, 50, 61-64, 69-79 |
| bread\_bot/common/schemas/api\_models.py                                               |       30 |        0 |    100.0% |           |
| bread\_bot/common/schemas/bread\_bot\_answers.py                                       |       22 |        0 |    100.0% |           |
| bread\_bot/common/schemas/commands.py                                                  |       28 |        0 |    100.0% |           |
| bread\_bot/common/schemas/telegram\_messages.py                                        |       62 |        0 |    100.0% |           |
| bread\_bot/common/services/commands/command\_parser.py                                 |      114 |       14 |     87.7% |64-65, 107-108, 127, 159-163, 182, 200, 206-207 |
| bread\_bot/common/services/commands/command\_settings.py                               |       28 |        0 |    100.0% |           |
| bread\_bot/common/services/handlers/answer\_handler.py                                 |      166 |       30 |     81.9% |45-61, 84, 87-92, 114, 117, 139, 152, 196, 199, 223, 251, 260 |
| bread\_bot/common/services/handlers/command\_handler.py                                |       28 |        6 |     78.6% |     37-42 |
| bread\_bot/common/services/handlers/command\_methods/admin\_command\_method.py         |      146 |       14 |     90.4% |50, 67-68, 71, 108, 119, 164-165, 198, 208-209, 220-221, 257 |
| bread\_bot/common/services/handlers/command\_methods/base\_command\_method.py          |       55 |       25 |     54.5% |     74-99 |
| bread\_bot/common/services/handlers/command\_methods/entertainment\_command\_method.py |      187 |       74 |     60.4% |46, 48, 50, 52, 54, 56, 63-64, 105-118, 121-139, 142-164, 171-174, 177-180, 183-186, 189-197, 212, 242 |
| bread\_bot/common/services/handlers/command\_methods/integration\_command\_method.py   |       41 |        2 |     95.1% |     21-22 |
| bread\_bot/common/services/handlers/command\_methods/member\_command\_method.py        |       68 |        4 |     94.1% |47-48, 80, 83 |
| bread\_bot/common/services/handlers/handler.py                                         |       36 |        1 |     97.2% |        26 |
| bread\_bot/common/services/member\_service.py                                          |      100 |        9 |     91.0% |52-53, 55-61, 155, 157, 159 |
| bread\_bot/common/services/messages/message\_receiver.py                               |       44 |        2 |     95.5% |    40, 51 |
| bread\_bot/common/services/messages/message\_sender.py                                 |       57 |       15 |     73.7% |33-45, 63, 84, 88, 90, 92, 94, 98-100 |
| bread\_bot/common/services/messages/message\_service.py                                |       42 |        3 |     92.9% |66, 73, 90 |
| bread\_bot/common/services/morph\_service.py                                           |       90 |        2 |     97.8% |    42, 98 |
| bread\_bot/common/services/think\_service.py                                           |       21 |        2 |     90.5% |     11-12 |
| bread\_bot/common/utils/functions.py                                                   |        4 |        0 |    100.0% |           |
| bread\_bot/common/utils/structs.py                                                     |       68 |        0 |    100.0% |           |
| bread\_bot/main/base\_client.py                                                        |       46 |        2 |     95.7% |     92-93 |
| bread\_bot/main/database/base.py                                                       |       12 |        0 |    100.0% |           |
| bread\_bot/main/database/mixins.py                                                     |      143 |       13 |     90.9% |39, 64-66, 120-122, 229-231, 256, 260, 285 |
| bread\_bot/main/procrastinate.py                                                       |        7 |        1 |     85.7% |         9 |
| bread\_bot/main/routes.py                                                              |        9 |        0 |    100.0% |           |
| bread\_bot/main/settings/default.py                                                    |       32 |        0 |    100.0% |           |
| bread\_bot/main/webserver.py                                                           |       20 |        0 |    100.0% |           |
| bread\_bot/utils/dependencies.py                                                       |       17 |        8 |     52.9% |21-25, 32-36 |
| bread\_bot/utils/helpers.py                                                            |       18 |        1 |     94.4% |        40 |
| bread\_bot/utils/json\_logger.py                                                       |       41 |        3 |     92.7% |46, 89, 95 |
| bread\_bot/utils/middlewares.py                                                        |      122 |       11 |     91.0% |80, 103-104, 203, 214-216, 239-240, 248-249 |
| bread\_bot/utils/testing\_tools.py                                                     |       35 |        4 |     88.6% |     35-39 |
| bread\_bot/utils/utils\_schemas.py                                                     |       38 |        0 |    100.0% |           |
|                                                                              **TOTAL** | **2435** |  **327** | **86.6%** |           |


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