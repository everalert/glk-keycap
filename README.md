# GLK

Galeforce Keycap Profile (GLK) is an MX-spaced, low-profile, semi-spherical, sculpted keycap inspired by the lack of OEM-style keycaps for low-profile switches. This profile aims to replicate the OEM feel, while adding a little spice inspired by other profiles.

GLK is developed in [CadQuery](https://github.com/CadQuery/cadquery) and released under the MIT License.

## Usage

Working with CadQuery is easiest to start with [CQ-Editor](https://github.com/CadQuery/CQ-editor), but running an instance of CadQuery Server via Docker provides a more stable and integrated experience.

**CQ-Editor**

1. Install dependencies via PIP with
	- `pip install --pre cadquery`
	- `pip install scipy git+https://github.com/gumyr/cq_warehouse.git#egg=cq_warehouse`
1. Download a pre-built CQ-Editor package from [jmwright's repository](https://github.com/jmwright/CQ-editor/actions?query=workflow%3Abuild).
1. Load `src/preview.py` in CQ-Editor and start rendering.

Note that because CQ-Editor runs an isolated version of Python, the additional dependencies installed via PIP may have version compatibility issues. CQ-Editor is also be prone to memory leaks in my experience. In either case, the best option is to work with Docker.

**Docker**

1. Create the image with `docker build -t cadquery/cadquery-server-warehouse .`
1. Run the container with
`docker run -t glk -p 5000:5000 -d -v $(pwd):/data cadquery/cadquery-server-warehouse run`
	- You can now remote into the container with VSCode to work locally.
1. View the CAD models in realtime at `http://localhost:5000`

Note that CadQuery Server will only automatically run scripts from `src` folder in this setup. See CadQuery Server's [github](https://github.com/roipoussiere/cadquery-server) for details on how you can configure it in step 2.

**Working with GLK**

The main ``keycap`` function in the ``src/GLK.py`` will produce a 1U home row key by default. The ``profile`` function will produce a dictionary containing all unique keycaps required for a 100% keyboard, and ErgoDox and a GLFCKB at official settings.

*some stuff about SLA printing support generation here*

*some stuff about GLK-S here*

**Examples**

*some stuff using the different features here*

**Save and Export results**

``src/export.py`` is setup generate STL and STEP files for a full keycap set via the ``profile`` function mentioned above, and will output to the `export` directory. See the file for some config options.

The `export` directory includes some examples of keycaps in both STL and STEP format, generated at modest quality settings.

## Credits

- **[OPK](https://github.com/cubiq/OPK) by matt3o** for teaching me about CadQuery
- **[LDSA](https://kbd.news/LDSA-keycap-profile-1377.html) by Darryl** for the deep dish inspiration
- **[Tilted keycap](https://twitter.com/bethesda2010yy/status/1567690873235972096) by bethesda2010yy** for inspiration to develop a simplified version
- **[CadQuery](https://github.com/CadQuery/cadquery)**
- **[CQ-Editor](https://github.com/CadQuery/CQ-editor)**
- **[CQ_Warehouse](https://github.com/gumyr/cq_warehouse) by gumyr**
- **[CadQuery Server](https://github.com/roipoussiere/cadquery-server) by roipoussiere**