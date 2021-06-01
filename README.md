![Docker Compose Actions Workflow](https://github.com/DaSKITA/tilter/workflows/Docker%20Compose%20Actions%20Workflow/badge.svg)

# tilter
Annotation tool _TILTer_ for the annotation and conversion of privacy policies into the [TILT schema](https://github.com/Transparency-Information-Language/schema).


## Run Application

### Prerequisites

* Python 3.7.0 or above

### Installation
1. Install [Docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/).
2. `git clone https://github.com/DaSKITA/tilter.git`
browser.


### SetUp

3. Type `docker-compose up` in the Terminal Window.
4. Access [http://localhost:5000](http://localhost:5000) and [http://localhost:5000/api/docs/](http://localhost:5000/api/docs/) in your favorite Browser
5. Get some Privacy Policies from the TUB-Cloud as `.txt`-files. And place them in the `data` folder.
6. Open a Terminal Window and activate your python environment.
7. Execute the script under `scripts/fill_database.sh`


__Note:__ You can also use the [feeder.py](/scripts/feeder.py) CLI drectly. For more Information run: `python feeder.py --help`. Make sure to install the required packages before.
The packages can be found in `scripts/fill_database.sh` after the `pip` command.

## Deployment

The TILTer ist currently deployed in a [google compute engine](http://34.89.190.55:5000/).
Deplyoment is not automated. Inside the engine the repository is clonded and has to be manually synched with
the remote repository. For access to the compute engine ask Michael, to provide you with the necessary
`ssh-keys` and Username.
The ssh-connection can be established via `ssh -i [Path_to_Private_Key] [USERNAME]@34.89.190.55`.
In the engine a log is created from the console output via nohub. All output is saved in `nohub.out` in the
root directory of the titler.

The deployment will be active for 90 days (from 31.05.2021) without any costs. Afterwards running the TILTer
will costs ~13 Euros per month.
## Versions

### v0.1
![](./.docs/screen1.png)

## Languages and Translations
Currently supported Languages are English (standard) and German. These are realized using the `pybabel` package. For more information regarding this topic please visit the [babel documentation](http://babel.pocoo.org/en/latest/index.html).

### Adding New Languages
New languages are added using the `pybabel` command as follows:
1. Append the code for the new Language to the `LANGUAGES`-list in `config.py`. For available language codes check the [babel documentation](http://babel.pocoo.org/en/latest/index.html).
2. Add new text to be translated using the `_([text])` command, where `[text]` is the string to be translated.
3. Execute `pybabel extract -F babel.cfg -o translations/messages.pot .` in `/app/`.
4. Execute `pybabel init -i translations/messages.pot -d translations -l [code]` in `app`, where `[code]` is the language code you chose in the first step.
5. Now add translations using `msgstr ""` entries in the file to `/app/translations/[code]/LC_MESSAGES/messages.po`, where `[code]` again is the language code you chose in the first step.
6. Compile the changes using `pybabel compile -d translations` in `/app/`.
7. Restart the flask application via docker.

### Updating Existing Languages
When updating existing languages there is no need to follow the whole procedure above. Instead use the following steps:
1. Add new text to be translated using the `_([text])` command, where `[text]` is the string to be translated.
2. Execute `pybabel extract -F babel.cfg -o translations/messages.pot .` in `/app/`.
3. Execute `pybabel update -i translations/messages.pot -d translations` in `/app/`.
4. Now add translations using `msgstr ""` entries in the file to `/app/translations/[code]/LC_MESSAGES/messages.po`, where `[code]` is the language code associated with the target language.
5. Compile the changes using `pybabel compile -d translations` in `/app/`.
6. Restart the flask application via docker.

## License
MIT License

2020

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### Dependencies
This software depends on the following third party software products:
- [label-studio](https://github.com/heartexlabs/label-studio-frontend) under Apache 2.0 License
- [bootstrap](https://github.com/twbs/bootstrap) under MIT License
- [flask](https://github.com/pallets/flask) under BSD-3-Clause License
