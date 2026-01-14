This project converts JMdictFurigana alignment data into bracketed furigana (i.e. 学校 → 学[がっ] 校[こう]) and then marks 音読み readings in katakana while keeping 訓読み in hiragana using KANJIDIC2. Output as a CSV suitable for importing into Anki, but the tooling is general-purpose and can be used for other dictionary processing workflows.

# License (Code)
All source code in this repository is licensed under the MIT License. See [LICENSE](./LICENSE).

# Data Sources & Attribution
This project does not bundle any upstream dictionary files. The build workflow downloads dictionary data from the original projects and generates outputs from that data.

**KANJIDIC2** (kanji readings; 音読み/訓読み metadata)\
[EDRDG KANJIDIC Project](https://www.edrdg.org/wiki/index.php/KANJIDIC_Project)

**JMdictFurigana** (furigana alignment data used to split readings by character)\
[JMdictFurigana](https://github.com/Doublevil/JmdictFurigana)

Please refer to the upstream projects for the authoritative license/terms of use and attribution requirements.

# Generated Outputs
This repository publishes generated `*.csv` and `*.apkg` files. These generated files are derived from upstream dictionary data such as JMdictFurigana, KANJIDIC2, and related EDRDG resources. As a result:

1. **The MIT License applies only to the code**, not to the upstream dictionary data.
2. The generated CSV/APKG files are **derivative works** of the upstream data and are therefore distributed under the license terms of the upstream sources, including any attribution requirements and restrictions.
3. If you redistribute the generated outputs, you are responsible for complying with the upstream licenses/terms.

# Disclaimer
This project is provided “as is”, without warranty of any kind.
Dictionary-derived readings and 音/訓 classifications may contain errors or ambiguities such as, but not limited to, 熟字訓, 当て字, rendaku, historical or ambiguous readings. Always verify critical information against authoritative references.
