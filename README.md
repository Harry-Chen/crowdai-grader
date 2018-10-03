# CrowdAI Grader

This project demonstrates how to write external graders for [CrowdAI](https://github.com/crowdai/CrowdAI).

## Requirements

* Python >= 3.6.5
* Flask >= 1.0.2 (PyPI)
* requests >= 2.19.1 (PyPI)

## Deployment

```bash
cp config.example.py config.py
vim config.py # set your own api url
flask run
```

In CrowdAI `config/application.yml`, set `GRADER` to the address and port that Flask is listening to.

Edit your chanllenge in CrowdAI, set `Grader Identifier` to the grader that you want to use (`random_grader` for default).

## Customization

To write your own grader, just create a file in `graders` which inherits `CommonGrader` class and overwrite the `grade` method to update the scores, and then register it in `config.py`. Note that orgnizer token should be used in grader, according to CrowdAI documentation.

One example named `RandomPointsGrader` is provided as reference.