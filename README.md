![Docker Compose Actions Workflow](https://github.com/DaSKITA/tilter/workflows/Docker%20Compose%20Actions%20Workflow/badge.svg)

# tilter
Annotation tool _TILTer_ for the annotation and conversion of privacy policies into the [TILT schema](https://github.com/Transparency-Information-Language/schema).

## Installation
1. Install [Docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/).
2. `git clone https://github.com/DaSKITA/tilter.git`
3. `docker-compose up`
5. Access [localhost:5000](localhost:5000) in your favorite browser.


## Versions

### v0.1
![](./.docs/screen1.png)

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
