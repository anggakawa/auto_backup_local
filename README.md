*read the disclaimer first [here](readme/DISC.md)* 

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

