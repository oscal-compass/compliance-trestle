# Compliance-trestle changelog


<!--next-version-placeholder-->

## v0.24.0 (2021-09-21)
### Feature
* Allow import to use the caching functionality to access external URLs (https/sftp etc) ([#718](https://github.com/IBM/compliance-trestle/issues/718)) ([`3527259`](https://github.com/IBM/compliance-trestle/commit/352725952687fde4627c97037e68f2238c638a04))

### Fix
* Update OCP compliance operator transform to use classes expected by IBM SCC.  ([`2068f57`](https://github.com/IBM/compliance-trestle/commit/2068f570ff6d47bb0348e630cd4dc01e2d90e4b5))
*  Correct split merge pathing inconsistencies. ([#725](https://github.com/IBM/compliance-trestle/issues/725)) ([`1ea7f63`](https://github.com/IBM/compliance-trestle/commit/1ea7f63549ad1f74a47572fb00f04f42bce2e5ab))
* Correct merge (including repository functionality) and improve merge cwd handling. ([#724](https://github.com/IBM/compliance-trestle/issues/724)) ([`a780e2c`](https://github.com/IBM/compliance-trestle/commit/a780e2ca16f8e5ca99a74e8167b6ccb66c3e91e1))

## v0.23.0 (2021-09-03)
### Feature
* Update of Oscal profile to osco from initial PoC with stakeholder review. ([`c47092a`](https://github.com/IBM/compliance-trestle/commit/c47092aecf0d4b73eef2147738832748ecb04b1a))
* Resolved profile catalog functionality and enhanced ssp generation ([#694](https://github.com/IBM/compliance-trestle/issues/694)) ([`193e3b9`](https://github.com/IBM/compliance-trestle/commit/193e3b9e8179d3be0b5eaa4692e9106c5e4ad628))
* Add new OSCAL profile-to-osco-yaml transformer functionality. ([#677](https://github.com/IBM/compliance-trestle/issues/677)) ([`c7e2156`](https://github.com/IBM/compliance-trestle/commit/c7e2156b9cc2546d15a70e7699091465c8a54e91))
* Adding rich model generation to trestle add and trestle create. ([#693](https://github.com/IBM/compliance-trestle/issues/693)) ([`9d32953`](https://github.com/IBM/compliance-trestle/commit/9d329530893da01de1b71dce8711fa3edb1fc2cb))
* Adding capability to allowing generator to generate optional fields. ([#690](https://github.com/IBM/compliance-trestle/issues/690)) ([`4a0f631`](https://github.com/IBM/compliance-trestle/commit/4a0f6318b426e24a2764e0a75edcaa84861cadd8))

### Fix
* Refactor underlying methods to isolate calls to Path.cwd() ([#716](https://github.com/IBM/compliance-trestle/issues/716)) ([`473c1d8`](https://github.com/IBM/compliance-trestle/commit/473c1d8ca85e688bd75362a3f0f22e8cc81c327d))
* Cleanup assemble command to reduce LoC covering the same functionality. ([#709](https://github.com/IBM/compliance-trestle/issues/709)) ([`c40cfca`](https://github.com/IBM/compliance-trestle/commit/c40cfca85af92c6e5d6c725ea069db4d534676f9))

## v0.22.1 (2021-08-19)
### Fix
* Strip back dependencies due to dependency error ([#684](https://github.com/IBM/compliance-trestle/issues/684)) ([`a8b4768`](https://github.com/IBM/compliance-trestle/commit/a8b476859cbc3ba77f9bf389ed2bb977bd80c592))
* Updating developer docs to include details on the CI workflow. ([#683](https://github.com/IBM/compliance-trestle/issues/683)) ([`e8d63e1`](https://github.com/IBM/compliance-trestle/commit/e8d63e1ddcfb9bf1b179de195bb86b7af7758fe3))

## v0.22.0 (2021-08-13)
### Feature
* Schema validate command including miscellaneous fixes. ([#665](https://github.com/IBM/compliance-trestle/issues/665)) ([`3ab088a`](https://github.com/IBM/compliance-trestle/commit/3ab088a9a9b4927a660510fe6fe8438a9b48fdfa))
* New command href and now ssp gen uses caching to pull catalog from remote ([#669](https://github.com/IBM/compliance-trestle/issues/669)) ([`660ef47`](https://github.com/IBM/compliance-trestle/commit/660ef47b48d17ce19ab31690ef8264afb085e326))

### Fix
* Improved error handling of yaml headers in markdown files. ([#676](https://github.com/IBM/compliance-trestle/issues/676)) ([`1983925`](https://github.com/IBM/compliance-trestle/commit/198392543a864ab213d869ddeaa123817d69b3c2))
* Documentation fixes as well as fixes to json serializisation for full utf-8 support. ([#674](https://github.com/IBM/compliance-trestle/issues/674)) ([`d051638`](https://github.com/IBM/compliance-trestle/commit/d0516381a8be4d4c97c14395965ade00f8181083))
* Relocate ParameterHelper class. ([#667](https://github.com/IBM/compliance-trestle/issues/667)) ([`0dbf472`](https://github.com/IBM/compliance-trestle/commit/0dbf472c5d3513fb85d66e4f76bb3bc037fc726f))

## v0.21.0 (2021-07-30)
### Feature
* Trestle Release #659 from IBM/develop ([`6329c82`](https://github.com/IBM/compliance-trestle/commit/6329c82ddd59e2699bd6e7dc8cd571e948fa21f6))
* Describe command to describe contents of model files with optional element path ([#650](https://github.com/IBM/compliance-trestle/issues/650)) ([`905ff8a`](https://github.com/IBM/compliance-trestle/commit/905ff8ac3cb0c7f11a8d8601bbcbcb2f9b40cae0))
* Spread sheet to component definition ([#635](https://github.com/IBM/compliance-trestle/issues/635)) ([`6fe4e22`](https://github.com/IBM/compliance-trestle/commit/6fe4e22ce9235e95ccd73c836bc8cbedfa99799c))

### Fix
* Ssp dropping section prose when in profile, now supporting profile & catalog section prose. ([#657](https://github.com/IBM/compliance-trestle/issues/657)) ([`4eadf47`](https://github.com/IBM/compliance-trestle/commit/4eadf475dc0ccd0f38bd365b9b71be90e6f98cce))
* Ssp section generation failed due to changes due to 1.0.0 ([#649](https://github.com/IBM/compliance-trestle/issues/649)) ([`26dac34`](https://github.com/IBM/compliance-trestle/commit/26dac345c65a59ef49f49af11dbacb1f2094ceb4))
* Split bugs and make -f optional ([#639](https://github.com/IBM/compliance-trestle/issues/639)) ([`c514301`](https://github.com/IBM/compliance-trestle/commit/c51430175117e1c1071442d3c564fae4afcef461))
* Cleanup and enhancement of linting. ([#636](https://github.com/IBM/compliance-trestle/issues/636)) ([`631eba9`](https://github.com/IBM/compliance-trestle/commit/631eba9ac1795bfcd109ed0e840898c2e6101528))

### Documentation
* Cross link documentation between compliance-trestle and compliance-trestle-demos repositories. ([#637](https://github.com/IBM/compliance-trestle/issues/637)) ([`f28aca1`](https://github.com/IBM/compliance-trestle/commit/f28aca1073888a7575a277c819449302e8e52b23))

## v0.20.0 (2021-07-16)
### Feature
* Adding a global option to trestle author headers. ([#628](https://github.com/IBM/compliance-trestle/issues/628)) ([`16f0265`](https://github.com/IBM/compliance-trestle/commit/16f0265b1296066a203a5f844d89fd642a00fdb6))
* Repository APIs to allow developer a consistent interface to a trestle repo. ([#583](https://github.com/IBM/compliance-trestle/issues/583)) ([`7bfabc5`](https://github.com/IBM/compliance-trestle/commit/7bfabc5a9e078cbfb6b190d3ccb7f06942d9ea37))

### Fix
* Added test cases for Repository code ([#625](https://github.com/IBM/compliance-trestle/issues/625)) ([`c3f8a33`](https://github.com/IBM/compliance-trestle/commit/c3f8a339bb66ea4723c9b1fa7b7ef30edf275cb5))
* Split catalog star, enable split of model with wildcard ([#626](https://github.com/IBM/compliance-trestle/issues/626)) ([`d17389e`](https://github.com/IBM/compliance-trestle/commit/d17389e824ce8f33f2a091cd541622fb40513a37))
* Tutorial tweaks ([#623](https://github.com/IBM/compliance-trestle/issues/623)) ([`3ab018d`](https://github.com/IBM/compliance-trestle/commit/3ab018d6dd63ae4ee98d90daca9b5580687ac8ae))
* Add gfm support for mdformat ([#620](https://github.com/IBM/compliance-trestle/issues/620)) ([`f67a74c`](https://github.com/IBM/compliance-trestle/commit/f67a74c63aedd1cabdb6fcfd8f5be99b25886949))
* Ssp assemble prose, all extraction of general prose for responses ([#618](https://github.com/IBM/compliance-trestle/issues/618)) ([`06e8627`](https://github.com/IBM/compliance-trestle/commit/06e862705bbf3880678324ba29e4be54e54322e6))
* Boost coverage fix split_too_fine ([#615](https://github.com/IBM/compliance-trestle/issues/615)) ([`891227b`](https://github.com/IBM/compliance-trestle/commit/891227b9899b38f7ce609f8b4b715740cb9a84f7))

## v0.19.0 (2021-07-06)
### Feature
* Merge pull request #611 from IBM/develop ([`0e9a4c5`](https://github.com/IBM/compliance-trestle/commit/0e9a4c51f75470c202efa53b625e3181bd31254c))
* Remove validate mode option and yaml_header optional in ssp-gen ([#607](https://github.com/IBM/compliance-trestle/issues/607)) ([`3a5e104`](https://github.com/IBM/compliance-trestle/commit/3a5e104d100feaad5334e8ee3231bdd6e93bbf82))
* Restore oscal write to use windows newlines on windows ([#608](https://github.com/IBM/compliance-trestle/issues/608)) ([`b7d8345`](https://github.com/IBM/compliance-trestle/commit/b7d83458a233204b52e4271ee908392870992d5c))
* Remove target model from trestle with OSCAL 1.0.0 release ([#595](https://github.com/IBM/compliance-trestle/issues/595)) ([`ececd37`](https://github.com/IBM/compliance-trestle/commit/ececd3792281b08bf26831acee1254bd24338815))

### Fix
* Remove incorrect scc_check_version in tanium transformer ([#591](https://github.com/IBM/compliance-trestle/issues/591)) ([`4c59eda`](https://github.com/IBM/compliance-trestle/commit/4c59edacfcacef2921711642776126a9b4e6a386))
* Duplicate oscal classes and reordered.  oscal_write line ending ([#592](https://github.com/IBM/compliance-trestle/issues/592)) ([`ddaeece`](https://github.com/IBM/compliance-trestle/commit/ddaeecebbf884f7b96509e3c75d798f65472278a))
* Ensure line endings do not change ([#593](https://github.com/IBM/compliance-trestle/issues/593)) ([`82fcab3`](https://github.com/IBM/compliance-trestle/commit/82fcab3ea5e4b06b6ff31a6e2749b30729cfd48d))

## v0.18.1 (2021-06-17)
### Fix
* Small scale fixes to the author validation system. (#572) ([#573](https://github.com/IBM/compliance-trestle/issues/573)) ([`04e16cc`](https://github.com/IBM/compliance-trestle/commit/04e16ccd508607eadb2c0ab4db69fb324cf0e24c))

## v0.18.0 (2021-06-17)
### Feature
* Allow explicit inclusion / exclusion of readme files in author workflows ([#570](https://github.com/IBM/compliance-trestle/issues/570)) ([`0ca1d20`](https://github.com/IBM/compliance-trestle/commit/0ca1d202fa4865acf20fb9156a9c13437350b16e))

### Fix
* Replace yaml library to ensure that errors are thrown / recognised on duplicate keys. ([#569](https://github.com/IBM/compliance-trestle/issues/569)) ([`9464420`](https://github.com/IBM/compliance-trestle/commit/9464420cb3bba1dc684051ff35e2d13e9a115203))

## v0.17.0 (2021-06-09)
### Feature
* Ssp generation of markdown files for groups of controls ([#556](https://github.com/IBM/compliance-trestle/issues/556)) ([`1dcf139`](https://github.com/IBM/compliance-trestle/commit/1dcf1395469b20b32e67c02cc52ede15d5b35f4b))
* Update `trestle md` to `trestle author` and introduce functionality for validating drawio metadata. ([#551](https://github.com/IBM/compliance-trestle/issues/551)) ([`2567e6c`](https://github.com/IBM/compliance-trestle/commit/2567e6c55039ce4b2db0d76fb4ae3c7495a26301))

### Fix
* Lint PR firing off dev ([#562](https://github.com/IBM/compliance-trestle/issues/562)) ([`81f44c6`](https://github.com/IBM/compliance-trestle/commit/81f44c628d687ab4f0d96b9c16d018459e9fc062))
* [ImgBot] Optimize images ([#560](https://github.com/IBM/compliance-trestle/issues/560)) ([`62b870d`](https://github.com/IBM/compliance-trestle/commit/62b870d3d98bf2a67be2c7fc68b0cf9e8d4b7f07))
* Allow for check suite to trigger a PR ([`5c95318`](https://github.com/IBM/compliance-trestle/commit/5c95318f8c43b6901d0992512e029d2aa584a73c))
* Allow for check suite to trigger a PR ([`9bce041`](https://github.com/IBM/compliance-trestle/commit/9bce041a02326d9e148ada7271eda5dbda46e504))
* Allow for test completion to trigger automerge correctly ([`dc6864f`](https://github.com/IBM/compliance-trestle/commit/dc6864f8a3bc03ec1f694d25dbeda19969507ab9))
* Correct github expression path. ([`9ab4936`](https://github.com/IBM/compliance-trestle/commit/9ab4936dc0aef7d4b2bd445dd4d8f1e3a13c6f9b))
* Ensrue automerge fires off correctly ([`d0f51b8`](https://github.com/IBM/compliance-trestle/commit/d0f51b841073d06269272f2e5f5a7f04bb07bc3a))
* CICD refinements ([`a2d836b`](https://github.com/IBM/compliance-trestle/commit/a2d836bc8e29d6cbe16346ed4172e258546e1196))
* Dump context in automerge workflow. ([`144a54f`](https://github.com/IBM/compliance-trestle/commit/144a54f8ef51252b4a4fec6117e85b388cd69b17))
* Cleanup CIDC workflow to prevent admin rights pushing over checks. ([`56127e7`](https://github.com/IBM/compliance-trestle/commit/56127e733dc0539d36e3faf32be1c3be701da1d8))
* Cleanup CIDC workflow to prevent admin rights pushing over checks. ([`a305ebb`](https://github.com/IBM/compliance-trestle/commit/a305ebb24c8595a0014afe1d6da5886400f1211b))
* Cleanup CIDC workflow to prevent admin rights pushing over checks. ([`31e8cde`](https://github.com/IBM/compliance-trestle/commit/31e8cde6b68009372a7dcf9562dc6e420ecec6d2))

## v0.16.0 (2021-05-28)
### Feature
* OSCO transformer conform to Results interface class. ([#532](https://github.com/IBM/compliance-trestle/issues/532)) ([`fc251b9`](https://github.com/IBM/compliance-trestle/commit/fc251b9e9c231de67fd214b16bdd7c2a6cb4d3c1))
* Functionaly complete ([`b7c903b`](https://github.com/IBM/compliance-trestle/commit/b7c903b703c78026ac14e31177cd4e3a7541d469))
* Oscal version validator ([#528](https://github.com/IBM/compliance-trestle/issues/528)) ([`2b132d5`](https://github.com/IBM/compliance-trestle/commit/2b132d5f09832452def258284bb40090d32bab01))
* Create title  - place names in title of created objects - issue #473 ([#519](https://github.com/IBM/compliance-trestle/issues/519)) ([`b676ed3`](https://github.com/IBM/compliance-trestle/commit/b676ed379b4328f3b69fe1806a7dad46ccc5319a))

### Fix
* Move unreachable debug statement ([`f5b9c1a`](https://github.com/IBM/compliance-trestle/commit/f5b9c1a029e6257c789ebc573105b582dca23e1b))
* Move unreachable debug statement ([`0ce9c24`](https://github.com/IBM/compliance-trestle/commit/0ce9c24a8fcc5e464f4194970e82740e6c0cd4f1))
* Complete coverage of drawio class ([`225403c`](https://github.com/IBM/compliance-trestle/commit/225403c4f85ca77cb322bb9620992ab0c6673e9b))
* Adding basic UT suite for drawio. ([`44cc8c3`](https://github.com/IBM/compliance-trestle/commit/44cc8c3fcb57bb23743fbe12d5bc180bf13edab5))
* Corrected errors ([`8187d6d`](https://github.com/IBM/compliance-trestle/commit/8187d6d5932669dddd676e68c24fe0d058703d52))
* Correcting errors ([`5bfedac`](https://github.com/IBM/compliance-trestle/commit/5bfedac6575d3e57ea530b0e69e55ebbcbb26c37))
* Improve devops to stop squash merging to main ([#542](https://github.com/IBM/compliance-trestle/issues/542)) ([`a8313fb`](https://github.com/IBM/compliance-trestle/commit/a8313fbf75b8c8eb5d2791b2dadafc1be03cc492))
* Remove problematic concurrency restrictions in devops pipeline ([#538](https://github.com/IBM/compliance-trestle/issues/538)) ([`5181c70`](https://github.com/IBM/compliance-trestle/commit/5181c70b44e283a21b4fedb05ecc36590d04c319))
* Stop split at strings, better handling of component-def splits ([#506](https://github.com/IBM/compliance-trestle/issues/506)) ([`43c9edd`](https://github.com/IBM/compliance-trestle/commit/43c9edd790579a7000a444a703b2d30a485480d1))
* Correct bad syntax in devops tooling. ([`dcec2ea`](https://github.com/IBM/compliance-trestle/commit/dcec2eaeacff7e7ad981e801255c844a37446390))
* Ensure PR automation system cannot override checks. ([#522](https://github.com/IBM/compliance-trestle/issues/522)) ([`5817316`](https://github.com/IBM/compliance-trestle/commit/5817316ff06cecba6b3662b96cb77655aa70277b))
* Correct semantic / conventional commit behaviour ([#520](https://github.com/IBM/compliance-trestle/issues/520)) ([`a6f7d01`](https://github.com/IBM/compliance-trestle/commit/a6f7d013998e0a198347d987558f7974e372b5ea))

### Documentation
* Reorg and cleanup content ([#531](https://github.com/IBM/compliance-trestle/issues/531)) ([`380e924`](https://github.com/IBM/compliance-trestle/commit/380e92476ff63126df470f31a4e8e0190e608fad))
* Updated third party schema as per latest tanium to oscal conversion and added it to documentation ([#527](https://github.com/IBM/compliance-trestle/issues/527)) ([`9feb690`](https://github.com/IBM/compliance-trestle/commit/9feb6908c80c3873cf310079144fbbbe20002c54))
* More google style doc strings ([#526](https://github.com/IBM/compliance-trestle/issues/526)) ([`28914f0`](https://github.com/IBM/compliance-trestle/commit/28914f088a78b57fdfb090eda662ea5c8b362884))
* Addtional documentation. ([#525](https://github.com/IBM/compliance-trestle/issues/525)) ([`516f01e`](https://github.com/IBM/compliance-trestle/commit/516f01eb0eff580bcfc95ea7b0909cd0ebdb8221))
* Small set of document updates ([#524](https://github.com/IBM/compliance-trestle/issues/524)) ([`7b339d7`](https://github.com/IBM/compliance-trestle/commit/7b339d7e81d0a2e626bc29c7718d0e1081996fbb))

## v0.15.1 (2021-05-20)
### Fix
* Trigger release ([#540](https://github.com/IBM/compliance-trestle/issues/540)) ([`aeffa5b`](https://github.com/IBM/compliance-trestle/commit/aeffa5b5aa1609b23fdbfed7d167068e366f72e9))

## v0.15.0 (2021-05-13)
### Feature
* Added error checking and enforce 1 to 1 keys in header validation ([#512](https://github.com/IBM/compliance-trestle/issues/512)) ([`da95862`](https://github.com/IBM/compliance-trestle/commit/da958620ffca76cbfae1762159a7ca51007c8b88))
* Role ID cross reference validator and refactors to validators to allow all ([`c894704`](https://github.com/IBM/compliance-trestle/commit/c894704875ae54e8376fb50d62cd064f1d293b66))
* Roleid validation via ncname and parametrized tests ([#499](https://github.com/IBM/compliance-trestle/issues/499)) ([`84dc9a2`](https://github.com/IBM/compliance-trestle/commit/84dc9a293e35f1c4010a38c7ecc8f99e5fa7dfb2))

### Fix
* Upgrade pydantic to 1.8.2 for security issue ([#513](https://github.com/IBM/compliance-trestle/issues/513)) ([`6e01f36`](https://github.com/IBM/compliance-trestle/commit/6e01f36cc6fdfd8b14d453f470968ad7ea4164fa))
* Remove problematic code-QL plugin which is causing problems. ([#507](https://github.com/IBM/compliance-trestle/issues/507)) ([`47529a7`](https://github.com/IBM/compliance-trestle/commit/47529a7714f0c99bb711033ca1863651de99dbf5))

## v0.14.4 (2021-04-22)
### Fix
* Add timestamp to tanium-to-oscal transformer ([#503](https://github.com/IBM/compliance-trestle/issues/503)) ([`e8dc204`](https://github.com/IBM/compliance-trestle/commit/e8dc204935b5d1f4584bcaaef77bba2c41d80a9f))

## v0.14.3 (2021-04-20)
### Fix
* Tanium updates for scc, 2 ([#498](https://github.com/IBM/compliance-trestle/issues/498)) ([`9b9b61e`](https://github.com/IBM/compliance-trestle/commit/9b9b61e6236da2f15cd6fc125925c6e4e708465f))

## v0.14.2 (2021-04-20)
### Fix
* Tanium enhancements for scc ([`8bae421`](https://github.com/IBM/compliance-trestle/commit/8bae421df04a7683bccc52ea40420bb85d4bcebe))

## v0.14.1 (2021-04-16)
### Fix
* Chore/fs cleanup ([#489](https://github.com/IBM/compliance-trestle/issues/489)) ([`bf8be03`](https://github.com/IBM/compliance-trestle/commit/bf8be03fc62e56928e8f92cfe746b004e0c54b71))

## v0.14.0 (2021-04-15)
### Feature
* Release of enhanced markdown functionality ([`f327fd6`](https://github.com/IBM/compliance-trestle/commit/f327fd67131c90afbe6c3644ab41b0dc56412b78))

## v0.13.1 (2021-04-13)
### Fix
* Force release. ([`0e90265`](https://github.com/IBM/compliance-trestle/commit/0e90265c7192979a613c30abd3561a68b612d8ac))

## v0.13.0 (2021-04-13)
### Feature
* Tanium to oscal tranform refactored to exploit the ResultsTransformer interface ([#466](https://github.com/IBM/compliance-trestle/issues/466)) ([`6fced57`](https://github.com/IBM/compliance-trestle/commit/6fced57a5c011aafb26220e94b038ebae884b20d))
* Update of OSCAL schema to 1.0.0-rc2 ([#465](https://github.com/IBM/compliance-trestle/issues/465)) ([`4e2f64d`](https://github.com/IBM/compliance-trestle/commit/4e2f64dd5a4f80f4081c0168b0e669b97dab79c8))

### Fix
* Cleanup of fs.py to allow relative and absolute paths ([#464](https://github.com/IBM/compliance-trestle/issues/464)) ([`1407911`](https://github.com/IBM/compliance-trestle/commit/140791190569e5673a216fe8dfdffc35d6c2424e))

## v0.12.0 (2021-04-09)
### Feature
* Release of transformation factory interface for beta testing. ([`a036522`](https://github.com/IBM/compliance-trestle/commit/a0365226175adfd38c5e37d863c4c50038a1658c))

## v0.11.0 (2021-04-08)
### Feature
* Update NIST models to latest including refactors & UT's ([`5a7a8a3`](https://github.com/IBM/compliance-trestle/commit/5a7a8a338ad3ef427f2ae9f26e2de4ac920fa525))
* Initial trestle markdown functionality. ([#407](https://github.com/IBM/compliance-trestle/issues/407)) ([`4d58e26`](https://github.com/IBM/compliance-trestle/commit/4d58e265392388c81549967384546ddad8f46e4e))
* Basics of HTTPS Fetcher for remote caching ([#421](https://github.com/IBM/compliance-trestle/issues/421)) ([`cbb43ae`](https://github.com/IBM/compliance-trestle/commit/cbb43ae4876a2015b0f10292c50268160b0a6dfd))

### Fix
* Issue 344 checked rc for commands in tests and removed dependency on dictdiffer ([#440](https://github.com/IBM/compliance-trestle/issues/440)) ([`acc337b`](https://github.com/IBM/compliance-trestle/commit/acc337b368602d5191244f973029b6ab02f212b2))
* Strangely behaving log lines ([#425](https://github.com/IBM/compliance-trestle/issues/425)) ([`2cca882`](https://github.com/IBM/compliance-trestle/commit/2cca88201e0fcd68419b72d04403a5baf1c1b33d))

## v0.10.0 (2021-03-25)
### Feature
* Adding exchange protocol as a supported 3rd party schema and object model. ([#416](https://github.com/IBM/compliance-trestle/issues/416)) ([`05b8781`](https://github.com/IBM/compliance-trestle/commit/05b8781283a32131ee0fd4a7097edef4bfdb6cb2))
* Added collection utilities. ([#413](https://github.com/IBM/compliance-trestle/issues/413)) ([`83c1f17`](https://github.com/IBM/compliance-trestle/commit/83c1f17e8902d969b07d9e3cf9fa1c80c22755c8))

### Fix
* Correcting more issues with load_distributed impacting trestle split and merge ([`6ccb4db`](https://github.com/IBM/compliance-trestle/commit/6ccb4db1614b521b9a132cbae17ac0922dea729b))
* Cleanup and add unit tests to the exchange_protocol module ([#417](https://github.com/IBM/compliance-trestle/issues/417)) ([`a194580`](https://github.com/IBM/compliance-trestle/commit/a19458008c5df39dbaf7bbcbfbc4431d16db4831))
* Merge updates - added version subcommand and modified load_distrib to load files by name ([#415](https://github.com/IBM/compliance-trestle/issues/415)) ([`0a22c83`](https://github.com/IBM/compliance-trestle/commit/0a22c833671a72f1d204eed50cb881e610ef0595))
* Correct OSCAL output to desired design point for osco-to-oscal. ([`5530eb4`](https://github.com/IBM/compliance-trestle/commit/5530eb4d334251b336a376a6b165b0874f43f391))
* Model behaviour correction and update to latest pydantic version. ([`fcbaa23`](https://github.com/IBM/compliance-trestle/commit/fcbaa2356dc2c7c53e3df1e5c7cd43b5c55c368b))

### Documentation
* Added more tutorials to the documentation for split and merge. ([`0bf275a`](https://github.com/IBM/compliance-trestle/commit/0bf275af173ac563147d73daaf5d500edd5c8729))
* Instructions for gen_oscal and fix_any added to website.md ([#389](https://github.com/IBM/compliance-trestle/issues/389)) ([`5053e52`](https://github.com/IBM/compliance-trestle/commit/5053e52e02e6f3761627b358b7e5abe107f17e21))

## v0.9.0 (2021-03-02)
### Feature
* Tanium export to oscal conversion task. ([`5f7bcbf`](https://github.com/IBM/compliance-trestle/commit/5f7bcbf885b5fcb77da054917b6e66fa83ce66e9))

### Fix
* Enforce oscal version in models and tests ([#377](https://github.com/IBM/compliance-trestle/issues/377)) ([`7fc08e1`](https://github.com/IBM/compliance-trestle/commit/7fc08e10b78b658359dc119080d64d44b09a572d))

## v0.8.1 (2021-02-24)
### Fix
* Import issues with hyphen named files ([#371](https://github.com/IBM/compliance-trestle/issues/371)) ([`07493ad`](https://github.com/IBM/compliance-trestle/commit/07493ad76f720503d756c54d67a1199abe181693))

## v0.8.0 (2021-02-22)
### Feature
* Added bulk operations for assemble ([#367](https://github.com/IBM/compliance-trestle/issues/367)) ([`771d54e`](https://github.com/IBM/compliance-trestle/commit/771d54e29ee839d38330929001c908b6ad669f8f))
* Utility to transform OSCO yaml data into OSCAL observations json data. ([#348](https://github.com/IBM/compliance-trestle/issues/348)) ([`488a75a`](https://github.com/IBM/compliance-trestle/commit/488a75a7fa5f259b2655b624ba7e3643c4ab7b28))
* Validate duplicates now loads distributed models ([#346](https://github.com/IBM/compliance-trestle/issues/346)) ([`1d54353`](https://github.com/IBM/compliance-trestle/commit/1d54353e595a502a3f1d0f4410f9da38f501daaa))

### Fix
* Allow assemble to succeed when no model is found. ([#368](https://github.com/IBM/compliance-trestle/issues/368)) ([`fe7a288`](https://github.com/IBM/compliance-trestle/commit/fe7a2882f447a628a30a08d1c089fac752d16579))
* To website automation test on windows ([#366](https://github.com/IBM/compliance-trestle/issues/366)) ([`8e3ecbf`](https://github.com/IBM/compliance-trestle/commit/8e3ecbf5f9acb8db4e200f7769cefcb20941a410))
* Fix merge main to back to develop automatically.(#332) ([`b64dd9f`](https://github.com/IBM/compliance-trestle/commit/b64dd9f5d1183109fe18bd3a75f5953af269d985))
* Corrected assemble to push files into the correct location. ([`f3bc0e5`](https://github.com/IBM/compliance-trestle/commit/f3bc0e5df22430d396ca0d82bc70624db34a6986))

### Documentation
* Website documentation for trestle task osco-to-oscal ([#336](https://github.com/IBM/compliance-trestle/issues/336)) ([`95c5c09`](https://github.com/IBM/compliance-trestle/commit/95c5c09b9f6f56aa4697609459f1369e06b7f3c2))

## v0.7.2 (2021-02-02)
### Fix
* DevOps fixes onto main ([#334](https://github.com/IBM/compliance-trestle/issues/334)) ([`74df375`](https://github.com/IBM/compliance-trestle/commit/74df375c15ad0bc2f0fb8c54e1ed83faf11d66e4))

## v0.7.1 (2021-02-02)
### Fix
* Assembly behaviour correction and devops fixes. ([`ac3828d`](https://github.com/IBM/compliance-trestle/commit/ac3828de66874807b70ee372be51976a724322d1))

## v0.7.0 (2021-01-28)
### Feature
* Trestle assemble implemented and documented. ([`e752bc2`](https://github.com/IBM/compliance-trestle/commit/e752bc2a6923c05c6251622499137d0c40633467))
* Enhancement to handle arboretum fetcher-built OSCO evidence as input ([#311](https://github.com/IBM/compliance-trestle/issues/311)) ([`e9c4196`](https://github.com/IBM/compliance-trestle/commit/e9c41969597c6bf587b5732e0851da3e7b24429e))
* Task osco-to-oscal to allow transformation from OpenSHift Compliance Operator to OSCAL ([#296](https://github.com/IBM/compliance-trestle/issues/296)) ([`ad995a2`](https://github.com/IBM/compliance-trestle/commit/ad995a22029aa67972bc9e6fdd3ebd0e987f50ba))
* Merge allows use of both yaml and json files. ([`4d87e6a`](https://github.com/IBM/compliance-trestle/commit/4d87e6aac5a49d1624da06d4f7bab4accb13b033))

### Fix
* Corrected bad link to website homepage. ([#314](https://github.com/IBM/compliance-trestle/issues/314)) ([`81124fb`](https://github.com/IBM/compliance-trestle/commit/81124fba5f25772cbcabf3fd0923ac6284794ff1))
* Corrected branch for mkdocs deploy. ([#304](https://github.com/IBM/compliance-trestle/issues/304)) ([`2dd5d93`](https://github.com/IBM/compliance-trestle/commit/2dd5d93df759f9bde345ca1f8d59014d8eb15787))

### Documentation
* Fix typos and grammar in cli and misspelling in split_merge docs ([#306](https://github.com/IBM/compliance-trestle/issues/306)) ([`272c2cc`](https://github.com/IBM/compliance-trestle/commit/272c2ccf6fbfca5fe6cdac7f0623b85fa8d5ddd7))

## v0.6.2 (2021-01-17)
### Fix
* Corrected branch for mkdocs deploy. (#304) ([#305](https://github.com/IBM/compliance-trestle/issues/305)) ([`be3f13a`](https://github.com/IBM/compliance-trestle/commit/be3f13a89d44c3f773ad7e372e4116eb609c8f5d))

## v0.6.1 (2021-01-15)
### Fix
* Extra unit tests and cleanup to close more significant gaps ([#298](https://github.com/IBM/compliance-trestle/issues/298)) ([`2abcaad`](https://github.com/IBM/compliance-trestle/commit/2abcaadc1bc14419111e1778bbb1fab61d633d5e))
* Changed split to not write empty files after split. Implemented circular split-merge test ([#295](https://github.com/IBM/compliance-trestle/issues/295)) ([`1ebbeb2`](https://github.com/IBM/compliance-trestle/commit/1ebbeb20db1e25852dd58f7fa7a4ed909e995ef0))

### Documentation
* Initial setup of documentation website. ([#234](https://github.com/IBM/compliance-trestle/issues/234)) ([`a51081b`](https://github.com/IBM/compliance-trestle/commit/a51081bd93cb43b02135b72f00e16cf805eacba9))

## v0.6.0 (2021-01-07)
### Feature
* Force update of version ([`fc0357b`](https://github.com/IBM/compliance-trestle/commit/fc0357b297bb59d64ad28af23fe2404c31364010))
* Update to OSCAL 1.0.0rc1 and simplified models. ([#286](https://github.com/IBM/compliance-trestle/issues/286)) ([`992b317`](https://github.com/IBM/compliance-trestle/commit/992b31743f4d1c4ce11d5b8c1ee69995856d0056))
* Distributed load and trestle merge.(#272) ([`dceae85`](https://github.com/IBM/compliance-trestle/commit/dceae854c9e96ef2e66931efa9a0263b0470003e))
* Misc cleanups of code for typing, unsafe functions, and other issues. ([#274](https://github.com/IBM/compliance-trestle/issues/274)) ([`0652392`](https://github.com/IBM/compliance-trestle/commit/06523929944351ce90ba83a85d57f0b04b323660))

### Fix
* Correct semantic release behaviour ([`c25d5be`](https://github.com/IBM/compliance-trestle/commit/c25d5be7448ee956cd848a1476b5c9c70d72ab33))
* Correct semantic release behaviour. ([`caba993`](https://github.com/IBM/compliance-trestle/commit/caba993013fed5b70ced84fc58d34345e042cb6c))
* Refactor to use python and pytest internals for temporary paths and creating directories. ([`1d99ca2`](https://github.com/IBM/compliance-trestle/commit/1d99ca2ac96d76dfa777a0c514be582b382504de))
* Small typo fix. ([`2168bb2`](https://github.com/IBM/compliance-trestle/commit/2168bb2b4d8fa79fbf93687a41265379cba608b8))

## v0.4.0 (2020-11-24)
### Feature
* Validation of duplicates now uses object factory (#216) ([`cf00f8b`](https://github.com/IBM/compliance-trestle/commit/cf00f8bb0ea4f0a7c039e1399525ede8d8d0ace8))
* Completed trestle create implementation. ([`a73538f`](https://github.com/IBM/compliance-trestle/commit/a73538f57f5bf4142c27f65a0b05834650f00cd7))

### Fix
* Additional test for trestle add (#227) ([`479413f`](https://github.com/IBM/compliance-trestle/commit/479413f1e0d4f90ae3c89833f71ce3fbd7a3db69))
* For issue 229, another Any] still present in file (#230) ([`428b270`](https://github.com/IBM/compliance-trestle/commit/428b270861873d5983551cd5a3d980e6dc728700))
* Improvements in typing and return codes. (#224) ([`c382cb5`](https://github.com/IBM/compliance-trestle/commit/c382cb593bf8b2f2b69810650320fdea544ed803))
* Refactor to adopt FileContentType consistently (#223) ([`793ea7c`](https://github.com/IBM/compliance-trestle/commit/793ea7c353e4445b9a8911f3455656403cca0ca0))
* Handle anomalous GroupItems that were generating empty classes (#220) ([`8fae9dc`](https://github.com/IBM/compliance-trestle/commit/8fae9dcc74f6067fe01fae0caee167e09a8b5d0f))
* Versioning tag was malformed. (#199) ([`5c84d59`](https://github.com/IBM/compliance-trestle/commit/5c84d59c539773b18709968405cbe77ce27e6a99))

### Documentation
* Updated developer documentation with DCO and merge workflow. ([`041a7aa`](https://github.com/IBM/compliance-trestle/commit/041a7aa8b2183a261827e5ee9d7d562849329e12))

## v0.3.0 (2020-10-26)
### Feature
* Implements `add` functionality for trestle cmd. (#184) ([`eb42656`](https://github.com/IBM/compliance-trestle/commit/eb42656c60c0697ff2de806d4a57ee7b246363de))

### Fix
* Versioning tag was malformed. (#199) (#200) ([`957fe0b`](https://github.com/IBM/compliance-trestle/commit/957fe0bf08a358e5ab21eb93c60dba65cc486b24))
* Support contextual element path like groups.* during split (#192) ([`c9536b2`](https://github.com/IBM/compliance-trestle/commit/c9536b2bcc6404fa9dab8787fcbf97e8590e4402))
* Correct directory names of sub models during split (#189) ([`6b18237`](https://github.com/IBM/compliance-trestle/commit/6b18237fda53f91f936fc122fdbf74da8e4db65e))
* Reference to inexistent function (#182) ([`9605a51`](https://github.com/IBM/compliance-trestle/commit/9605a5101507e3d1c79218328424bdf115c435ca))
* Infer wrapper alias from input in Element constructor ([`82820fd`](https://github.com/IBM/compliance-trestle/commit/82820fde423c1982a5aa02965d897f04093187bb))
* Explicitly use contextual_model argument in path parsing util function ([`1ae3b12`](https://github.com/IBM/compliance-trestle/commit/1ae3b12e8a3786aa8f7516ca631070fb289be949))
* Do not create empty place holder file after splitting a dict or list ([`cb9fa8b`](https://github.com/IBM/compliance-trestle/commit/cb9fa8be810c915198b094785ce581b89a54ce99))
* Create main model alias directory during split ([`7656e42`](https://github.com/IBM/compliance-trestle/commit/7656e420acedf5b2e61c5fb27b448196a362c521))
* Incorrect file indexing during split #148 ([`ad7b2e6`](https://github.com/IBM/compliance-trestle/commit/ad7b2e63125fa3508254bd0c579e072f1e260fad))
* Utility method to write/read Oscal List and Dict object to/from file correctly (#161) ([`43c7bdf`](https://github.com/IBM/compliance-trestle/commit/43c7bdf5c30d88056999776e5df5fc9957842122))
* Updating fetch of NIST content. ([`85a852a`](https://github.com/IBM/compliance-trestle/commit/85a852a20fa33c1546a7f6cc64201809fb845fea))
* Merge pull request #158 from IBM/fix/issue_149b ([`75b11ca`](https://github.com/IBM/compliance-trestle/commit/75b11ca91e0a23778511ac285b4655fbe12bd9f8))

### Documentation
* Initial caching structure documentation (#143) ([`d1a73f3`](https://github.com/IBM/compliance-trestle/commit/d1a73f314d42201fb7b9cbe79775a41b465ef6c7))
* Updated readme to document current level of support for file formats (#179) ([`1df2110`](https://github.com/IBM/compliance-trestle/commit/1df2110eb9fb89816871ce70ceb72d5f3be18049))
* Change of trestle model directory structure (#169) ([`ed2ab36`](https://github.com/IBM/compliance-trestle/commit/ed2ab36c64ddb45297974bb851819322477c0fd2))