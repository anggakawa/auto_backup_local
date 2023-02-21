~~~
This custom method has been developed based on the [auto_backup](https://github.com/OCA/server-tools/tree/15.0/auto_backup) module from the OCA (Odoo Community Association) for Odoo. It has been created for specific purposes and may not be suitable for every use case.

The author of this custom method makes no warranty or representation, either express or implied, about the accuracy, reliability, or suitability of the software for any purpose. The software is provided "as is" without warranty of any kind, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement.

In no event shall the author be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including but not limited to procurement of substitute goods or services, loss of use, data, or profits, or business interruption) arising in any way out of the use of this software, even if advised of the possibility of such damage.

The user assumes full responsibility and risk of using this software. The author shall not be liable for any claims or damages whatsoever, including property damage, personal injury, intellectual property infringement, loss of profits, or interruption of business, arising from the use or inability to use this software.

Use of this software indicates acceptance of the terms of this disclaimer.
~~~


# Database Auto-Backup

A tool for all your back-ups, internal only!

## Installation
---

~~Before installing this module, you need to execute::~~
   ~~pip3 install pysftp==0.2.9~~

No need to install external libraries because it is local only.


## Configuration
---

Go to *Settings -> Database Structure -> Automated Backup* to
create your configurations for each database that you needed
to backups.

## Usage
---

Keep your Odoo data safe with this module. Take automated back-ups,
remove them automatically.


## Known issues / Roadmap
---

* On larger databases, it is possible that backups will die due to Odoo server settings. In order to circumvent this without frivolously changing settings, you need to run the backup from outside of the main Odoo instance. How to do this is outlined in [this blog post](https://blog.laslabs.com/2016/10/running-python-scripts-within-odoos-environment).
* ~~Backups won't work if list_db=False is configured in the instance.~~

## Bug Tracker
---

Do not contact contributors directly about support or help with technical issues.

## Credits
---

### Authors
~~~

* Yenthe Van Ginneken
* Agile Business Group
* Grupo ESOC Ingenieria de Servicios
* LasLabs
* AdaptiveCity

~~~

### Contributors
~~~

* Yenthe Van Ginneken <yenthe.vanginneken@vanroey.be>
* Alessio Gerace <alessio.gerace@agilebg.com>
* Jairo Llopis <yajo.sk8@gmail.com>
* Dave Lasley <dave@laslabs.com>
* Andrea Stirpe <a.stirpe@onestein.nl>
* Aitor Bouzas <aitor.bouzas@adaptivecity.com>
* Simone Vanin <simone.vanin@agilebg.com>
* Vu Nguyen Anh <vuna2004@gmail.com>

## Maintainers
---
This module is an modified version from (auto_backup )[https://github.com/OCA/server-tools/tree/15.0/auto_backup]

