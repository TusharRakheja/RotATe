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
- When done, you can open the resulting csv file in Excel and trim the target name, sort by p-value etc.

| **Target** | **Source 1**       | **Source 2**     | **Source 3**    | **Source 4**      | **Weight 1** | **Weight 2** | **Weight 3** | **Weight 4** | **Error 1** | **Error 2** | **Error 3** | **Error 4** | **p-value**  |
| ---------- | ------------------ | ---------------- | --------------- | ----------------- | ------------ | ------------ | ------------ | ------------ | ----------- | ----------- | ----------- | ----------- | ------------ |
| I11456     | Laos_Hoabinhian.SG | Iran_GanjDareh_N | CHN_Tarim_EMBA1 | Turkey_N          | 33.40%       | 46.70%       | 11.50%       | 8.40%        | 1.70%       | 2.90%       | 1.30%       | 2.10%       | 0.268896     |
| I11456     | Laos_Hoabinhian.SG | Iran_GanjDareh_N | TTK             | Levant_PPN        | 34.60%       | 44.20%       | 12.40%       | 8.90%        | 1.70%       | 3.00%       | 1.40%       | 2.00%       | 0.172829     |
| I11456     | Laos_Hoabinhian.SG | Iran_GanjDareh_N | TTK             | Turkey_N          | 35.60%       | 44.20%       | 12.60%       | 7.60%        | 1.70%       | 3.10%       | 1.40%       | 2.10%       | 0.156486     |
| I11456     | Laos_Hoabinhian.SG | Iran_GanjDareh_N | CHN_Tarim_EMBA1 | Levant_PPN        | 32.50%       | 46.70%       | 11.10%       | 9.80%        | 1.70%       | 2.80%       | 1.30%       | 2.00%       | 0.154033     |
| I11456     | Laos_Hoabinhian.SG | Iran_GanjDareh_N | CHN_Tarim_EMBA1 | Turkey_Boncuklu_N | 33.00%       | 46.60%       | 11.00%       | 9.30%        | 1.70%       | 2.80%       | 1.30%       | 1.90%       | 0.152052     |
| I11456     | Laos_Hoabinhian.SG | Iran_Wezmeh_N.SG | CHN_Tarim_EMBA1 | Turkey_N          | 29.00%       | 49.90%       | 15.10%       | 6.10%        | 1.80%       | 2.30%       | 1.30%       | 2.00%       | 0.107075     |
| I11456     | Laos_Hoabinhian.SG | Iran_GanjDareh_N | TTK             | Turkey_Boncuklu_N | 35.20%       | 44.30%       | 12.20%       | 8.40%        | 1.70%       | 3.00%       | 1.40%       | 1.90%       | 0.100162     |
| I11456     | ONGE.SG            | Iran_Wezmeh_N.SG | CHN_Tarim_EMBA1 | Turkey_N          | 26.80%       | 51.00%       | 15.40%       | 6.80%        | 1.70%       | 2.30%       | 1.30%       | 2.10%       | 0.091318     |
| I11456     | Laos_Hoabinhian.SG | Iran_Wezmeh_N.SG | WSHG            | Turkey_N          | 30.40%       | 50.90%       | 14.90%       | 3.70%        | 1.70%       | 2.30%       | 1.30%       | 2.10%       | 0.072596     |
| I11456     | ONGE.SG            | Iran_Wezmeh_N.SG | CHN_Tarim_EMBA1 | Turkey_Boncuklu_N | 26.30%       | 50.90%       | 14.80%       | 8.00%        | 1.70%       | 2.10%       | 1.30%       | 1.60%       | 0.068768     |
| I11456     | Laos_Hoabinhian.SG | Iran_Wezmeh_N.SG | CHN_Tarim_EMBA1 | Turkey_Boncuklu_N | 28.40%       | 49.50%       | 14.40%       | 7.70%        | 1.80%       | 2.10%       | 1.30%       | 1.60%       | 0.068531     |
| I11456     | ONGE.SG            | Iran_Wezmeh_N.SG | WSHG            | Turkey_N          | 28.30%       | 52.10%       | 15.00%       | 4.60%        | 1.60%       | 2.30%       | 1.30%       | 2.10%       | 0.051668     |
| I11456     | ONGE.SG            | Iran_GanjDareh_N | CHN_Tarim_EMBA1 | Turkey_N          | 30.30%       | 46.70%       | 12.50%       | 10.50%       | 1.70%       | 2.70%       | 1.30%       | 2.00%       | 0.046209     |
| I11456     | Laos_Hoabinhian.SG | Iran_GanjDareh_N | WSHG            | Turkey_N          | 34.40%       | 48.10%       | 11.20%       | 6.40%        | 1.70%       | 2.80%       | 1.30%       | 2.10%       | 0.0399       |
| I11456     | Laos_Hoabinhian.SG | Iran_Wezmeh_N.SG | CHN_Tarim_EMBA1 | Levant_PPN        | 28.40%       | 48.70%       | 14.60%       | 8.30%        | 1.80%       | 2.20%       | 1.30%       | 1.80%       | 0.034571     |
| I11456     | Laos_Hoabinhian.SG | Iran_Wezmeh_N.SG | WSHG            | Turkey_Boncuklu_N | 29.90%       | 50.20%       | 13.90%       | 6.00%        | 1.70%       | 2.20%       | 1.30%       | 1.70%       | 0.023013     |
| I11456     | ONGE.SG            | Iran_GanjDareh_N | CHN_Tarim_EMBA1 | Turkey_Boncuklu_N | 30.20%       | 47.00%       | 12.10%       | 10.70%       | 1.60%       | 2.70%       | 1.30%       | 1.80%       | 0.022325     |
| I11456     | ONGE.SG            | Iran_Wezmeh_N.SG | CHN_Tarim_EMBA1 | Levant_PPN        | 26.00%       | 50.50%       | 15.20%       | 8.30%        | 1.70%       | 2.20%       | 1.30%       | 1.80%       | 0.021185     |
| I11456     | ONGE.SG            | Iran_Wezmeh_N.SG | WSHG            | Turkey_Boncuklu_N | 27.80%       | 51.70%       | 14.10%       | 6.40%        | 1.60%       | 2.10%       | 1.30%       | 1.70%       | 0.021096     |
| I11456     | Laos_Hoabinhian.SG | Iran_Wezmeh_N.SG | WSHG            | Levant_PPN        | 29.90%       | 49.50%       | 14.10%       | 6.50%        | 1.70%       | 2.20%       | 1.30%       | 1.80%       | 0.016969     |
| I11456     | Laos_Hoabinhian.SG | Iran_GanjDareh_N | WSHG            | Turkey_Boncuklu_N | 33.80%       | 48.10%       | 10.50%       | 7.60%        | 1.70%       | 2.80%       | 1.30%       | 1.90%       | 0.016734     |
| I11456     | Laos_Hoabinhian.SG | Iran_Wezmeh_N.SG | TTK             | Turkey_N          | 32.80%       | 46.10%       | 15.50%       | 5.60%        | 1.70%       | 2.40%       | 1.40%       | 2.10%       | 0.016642     |
| I11456     | Laos_Hoabinhian.SG | Iran_GanjDareh_N | WSHG            | Levant_PPN        | 33.40%       | 48.10%       | 10.50%       | 7.90%        | 1.70%       | 2.80%       | 1.30%       | 1.90%       | 0.014936     |
| I11456     | ONGE.SG            | Iran_GanjDareh_N | CHN_Tarim_EMBA1 | Levant_PPN        | 29.10%       | 47.80%       | 12.20%       | 10.90%       | 1.70%       | 2.70%       | 1.30%       | 1.90%       | 0.013477     |
| I11456     | ONGE.SG            | Iran_Wezmeh_N.SG | WSHG            | Levant_PPN        | 27.60%       | 51.30%       | 14.50%       | 6.70%        | 1.60%       | 2.20%       | 1.30%       | 1.80%       | 0.012671     |
| I11456     | ONGE.SG            | Iran_GanjDareh_N | TTK             | Turkey_N          | 32.90%       | 44.10%       | 13.20%       | 9.80%        | 1.70%       | 3.00%       | 1.40%       | 2.10%       | 0.012575     |
| I11456     | Laos_Hoabinhian.SG | Iran_Wezmeh_N.SG | TTK             | Levant_PPN        | 32.00%       | 45.00%       | 15.20%       | 7.80%        | 1.70%       | 2.30%       | 1.40%       | 1.80%       | 0.012301     |
| I11456     | Laos_Hoabinhian.SG | Iran_Wezmeh_N.SG | TTK             | Turkey_Boncuklu_N | 32.10%       | 46.00%       | 14.90%       | 7.00%        | 1.70%       | 2.30%       | 1.40%       | 1.60%       | 0.010389     |
| I11456     | ONGE.SG            | Iran_GanjDareh_N | TTK             | Turkey_Boncuklu_N | 32.70%       | 44.60%       | 12.70%       | 9.90%        | 1.60%       | 2.90%       | 1.40%       | 1.90%       | 0.007417     |
| I11456     | ONGE.SG            | Iran_Wezmeh_N.SG | TTK             | Turkey_N          | 30.50%       | 47.50%       | 15.50%       | 6.50%        | 1.60%       | 2.40%       | 1.40%       | 2.10%       | 0.006757     |
| I11456     | ONGE.SG            | Iran_GanjDareh_N | TTK             | Levant_PPN        | 31.60%       | 45.30%       | 13.00%       | 10.10%       | 1.60%       | 2.90%       | 1.40%       | 1.90%       | 0.005977     |
| I11456     | ONGE.SG            | Iran_Wezmeh_N.SG | TTK             | Turkey_Boncuklu_N | 30.00%       | 47.60%       | 14.80%       | 7.50%        | 1.60%       | 2.20%       | 1.40%       | 1.70%       | 0.005682     |
| I11456     | ONGE.SG            | Iran_GanjDareh_N | WSHG            | Turkey_N          | 31.30%       | 48.30%       | 12.00%       | 8.30%        | 1.70%       | 2.70%       | 1.30%       | 2.00%       | 0.003366     |
| I11456     | ONGE.SG            | Iran_Wezmeh_N.SG | TTK             | Levant_PPN        | 29.60%       | 47.10%       | 15.30%       | 7.90%        | 1.60%       | 2.30%       | 1.40%       | 1.80%       | 0.002799     |
| I11456     | ONGE.SG            | Iran_GanjDareh_N | WSHG            | Turkey_Boncuklu_N | 31.00%       | 48.80%       | 11.40%       | 8.80%        | 1.60%       | 2.70%       | 1.30%       | 1.80%       | 0.001487     |
| I11456     | ONGE.SG            | Iran_GanjDareh_N | WSHG            | Levant_PPN        | 30.20%       | 49.20%       | 11.60%       | 9.00%        | 1.60%       | 2.70%       | 1.30%       | 1.80%       | 0.000874     |
