This project converts JMdictFurigana alignment data into bracketed furigana (i.e. 学校 → 学[がっ] 校[こう]) and then converts 音読み readings to katakana using KANJIDIC2. Output as a CSV, the tooling is general-purpose and can be used for other dictionary processing workflows.

Mistakes and misclassification reports are welcome — please open an issue.

# Features
- can account for <ruby>促<rt>そく</rt>音<rt>おん</rt></ruby> readings
- correctly identifies readings of repeated kanji using the 々 character
- correctly handles voice readings (はん→ばん)
- normalises JMDictFurigana entries to hiragana to prevent premature false-negatives
- deals with non-official renyoukei (noun-from-verb) readings
- can add manual `additional_kanji_readings.csv` and `manual_onkunyomi.csv` files to fix individual cases
- correctly handles mizenkei (上げる→上げ)
- filters out entries that don't contain kanji or are metkanji (々〆)
- handles abbreviated kun readings misclassified as onyomi<br>うなぎ丼[どんぶり] (correct)<br>うな丼[ドン] (abbreviation of kun reading mistaken as rendaku of on reading) (wrong)

# Tags
| tag                        | meaning                                                                                                                                                                                                                                                |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `on`                       | at least one `kanji[reading]` segment was classified as on-yomi. converted to katakana.                                                                                                                                                                |
| `kun`                      | at least one `kanji[reading]` segment was classified as kun-yomi. no change.                                                                                                                                                                           |
| `unknown`                  | 1. one or more `kanji[reading]` segments could not be matched to either on or kun readings in KANJIDIC2. no change.<br>2. one or more 々 characters were found but no repeated kanji could be identified                                               |
| `ambiguous`                | one or more `kanji[reading]` segments matched both the computed on and kun variants sets for that kanji. unique classification not possible. no change.                                                                                                |
| `irregular`                | 1. the mapping included a multi-kanji bracket segment (e.g. 今日[きょう])<br>2. the dictionary bracket-building mapping had a multi-character span (e.g. 3-4)<br><br>assumed to be an ateji, jukujikun or nanori reading. classification not attemped. |
| `source_katakana`          | the original bracket reading in the source dictionary contained katakana. usually indicates gairaigo. no change.                                                                                                                                       |
| `manual_onkunyomi`         | a word-specific override from `manual_onkunyomi.csv` was applied                                                                                                                                                                                       |
| `additional_kanji_reading` | a kanji-level override from `additional_kanji_readings.csv` was applied                                                                                                                                                                                |
| `suspect_abbrev`           | an on-classified kanji reading that is a proper prefix of one or more of that kanji's kun readings was identified. used to find likely abbreviations of kun readings that may be misclassified as on. no change.                                       |
| `abbrev_on_to_kun`         | treated a `suspect_abbrev` case as kun. automatically changed classification to kun.                                                                                                                                                                   |

# Stats
| version        | count   | `tag:unknown`      | `tag:ambiguous`  | `tag:irregular`  | `-tag:unknown`<br>`-‍tag:ambiguous` | `tag:unknown` or `tag:ambiguous` | overlap        |
| -------------- | ------- | ------------------ | ---------------- | ---------------- | ---------------------------------- | -------------------------------- | -------------- |
| poc            | 229,833 | 34,410<br>(14.97%) | 5,915<br>(2.57%) | 6,534<br>(2.84%) | 189,926<br>(82.64%)                | 39,907<br>(17.36%)               | 418<br>(0.18%) |
| 令和8年1月26日 | 228,277 | 5,825<br>(2.55%)   | 6,097<br>(2.67%) | 6,534<br>(2.86%) | 216,407<br>(94.80%)                | 11,870<br>(5.20%)                | 52<br>(0.02%)  |

# Future Releases
Dictionary entries that are believed to be input errors or furigana misalignments will be filtered out before classification not included in the final `.csv`.

# Legal
## License (Code)
All source code in this repository is licensed under the MIT License. See [LICENSE](./LICENSE).

## Data Sources & Attribution
This project does not bundle any upstream dictionary files. The build workflow downloads dictionary data from the original projects and generates outputs from that data.

**KANJIDIC2** (kanji readings; 音読み/訓読み metadata)\
[EDRDG KANJIDIC Project](https://www.edrdg.org/wiki/index.php/KANJIDIC_Project)

**JMdictFurigana** (furigana alignment data used to split readings by character)\
[JMdictFurigana](https://github.com/Doublevil/JmdictFurigana)

Please refer to the upstream projects for the authoritative licenses, terms of use and attribution requirements.

## Generated Outputs
This repository publishes `*.csv` and `*.apkg` files generated from the provided `onkunfuri.py` file. These generated files are derived from upstream dictionary data such as JMdictFurigana, KANJIDIC2, and related EDRDG resources. As a result:

1. **The MIT License applies only to the code**, not to the upstream dictionary data.
2. The generated CSV and APKG files may be considered **derivative works** and are therefore distributed under the license terms of the upstream sources, including any attribution requirements and restrictions.
3. If you redistribute the generated outputs, you are responsible for complying with the upstream licenses and terms.

## Disclaimer
This project is provided “as is”, without warranty of any kind.
Dictionary-derived readings and 音/訓 classifications may contain errors or ambiguities such as, but not limited to, 熟字訓, 当て字, 連濁 and historical or ambiguous readings. Always verify critical information against authoritative references.
