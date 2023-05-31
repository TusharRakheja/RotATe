<img src="https://github.com/TusharRakheja/rotATe/raw/main/title.png" width="auto" height="100px" />

___

**rotAte** is a script to run rotating qpAdm models using [AdmixTools](https://github.com/DReichLab/AdmixTools)

### Dependencies

- Python 3.8+
- AdmixTools

### Usage

- Place the `rotate.py` script in your `tools` directory. This is the same directory that contains the `.ind`, `.snp`, and `.geno` files.
- Make a config file after the example `config.yml` in the repo, containing your target, your core sources, and your rotating sources. For example:

**Note**: All sources as well as the target should be present in the `.ind` file.

```yaml
core_right:
  - "Mbuti.DG"
  - "Russia_Ust_Ishim.DG"
  - "China_Tianyuan"
  - "ANE"
  - "Israel_Natufian"
  - "WHG"
  - "Iran_Mesolithic_BeltCave_noUDG"
  - "EHG"
  - "Serbia_IronGates_Mesolithic"
  - "Mongolia_North_N"

target: "Iran_ShahrISokhta_BA2"

sources:
  -
    - "ONGE.SG"
    - "Laos_Hoabinhian.SG"  
  -
    - "Iran_GanjDareh_N"
    - "Iran_Wezmeh_N.SG"
  -
    - "TTK"
    - "CHN_Tarim_EMBA1"
    - "WSHG"
  -
    - "Turkey_N"
    - "Turkey_Boncuklu_N"
    - "Levant_PPN"
```

- Run the script with `python3 ./rotate.py`. You can tail the results using `tail -f ./results.csv`.

