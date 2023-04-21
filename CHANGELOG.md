# Compliance-trestle changelog


<!--next-version-placeholder-->

## v2.1.0 (2023-04-06)
### Feature
* Validate SSP rule parameter values ([#1337](https://github.com/IBM/compliance-trestle/issues/1337)) ([`10dd58b`](https://github.com/IBM/compliance-trestle/commit/10dd58b552f8f9a4618daea27e6d0ccd002dbd80))
* Adds implementation status to ssp-filter ([#1338](https://github.com/IBM/compliance-trestle/issues/1338)) ([`c33fc7d`](https://github.com/IBM/compliance-trestle/commit/c33fc7d2ac9b430349962a08263db94c660a5f1c))
* Remove root references ([#1316](https://github.com/IBM/compliance-trestle/issues/1316)) ([`0dfdc79`](https://github.com/IBM/compliance-trestle/commit/0dfdc797090a5ccbc64b6ba0e2b2dd16464a65ae))

### Fix
* Comply with IBM Github action policy ([#1344](https://github.com/IBM/compliance-trestle/issues/1344)) ([`dd118f8`](https://github.com/IBM/compliance-trestle/commit/dd118f84a26ce0e83cc4249837f91a118ae1f487))
* Duplicate param_id should be invalid only in profile ([#1341](https://github.com/IBM/compliance-trestle/issues/1341)) ([`0edbd81`](https://github.com/IBM/compliance-trestle/commit/0edbd81efdb164f56d90972aca8bbf7539a6ba57))
* Remove components from ssp during ssp-assemble and give warning ([#1327](https://github.com/IBM/compliance-trestle/issues/1327)) ([`03d4f05`](https://github.com/IBM/compliance-trestle/commit/03d4f05a1d0bb0ef7c81e768238b67ae5cfbf5ca))
* Get_control_response was missing prose if statement has no parts ([#1335](https://github.com/IBM/compliance-trestle/issues/1335)) ([`04c39d4`](https://github.com/IBM/compliance-trestle/commit/04c39d4fb2911456c93495dce743cf971dec6f82))
* Better error handling when no comps specified during ssp-assemble - and added docs ([#1328](https://github.com/IBM/compliance-trestle/issues/1328)) ([`2ecdb98`](https://github.com/IBM/compliance-trestle/commit/2ecdb987f22f3da4592acd636637134161f05a0b))
* Ssp assemble includes controls not in the profile ([#1325](https://github.com/IBM/compliance-trestle/issues/1325)) ([`138e95f`](https://github.com/IBM/compliance-trestle/commit/138e95fd0598008b082fdf79a0306f68979c2c8e))
* Version test ([#1313](https://github.com/IBM/compliance-trestle/issues/1313)) ([`3c1d7bb`](https://github.com/IBM/compliance-trestle/commit/3c1d7bb439deab94851d2d0eb3b6a6766a0b5601))

### Documentation
* Fix refs to version numbers and update docs ([#1326](https://github.com/IBM/compliance-trestle/issues/1326)) ([`525f0f8`](https://github.com/IBM/compliance-trestle/commit/525f0f80de39dfe230ab3d95486533ab72473980))

## v2.0.0 (2023-03-01)
### Feature
* Cd resolved profile controls check ([#1309](https://github.com/IBM/compliance-trestle/issues/1309)) ([`638dd53`](https://github.com/IBM/compliance-trestle/commit/638dd5384c6588ad9bb88726c8d716cfc6e4b03b))
* Add ability to view version of the individual OSCAL object ([#1298](https://github.com/IBM/compliance-trestle/issues/1298)) ([`cf2af61`](https://github.com/IBM/compliance-trestle/commit/cf2af617fad82ccdfbebcd48948dd8a67512e7aa))
* New format csv to oscal component definition ([#1285](https://github.com/IBM/compliance-trestle/issues/1285)) ([`9572c4b`](https://github.com/IBM/compliance-trestle/commit/9572c4b83c03eaec6518333670fa8d6c80cafbf2))
* Allow remote profiles to reference catalogs and profiles by relative path in href ([#1288](https://github.com/IBM/compliance-trestle/issues/1288)) ([`0a7e2cf`](https://github.com/IBM/compliance-trestle/commit/0a7e2cf47680c19ef406aeb49afc35412478fc57))
* CIS spread sheet to OSCAL catalog ([#1270](https://github.com/IBM/compliance-trestle/issues/1270)) ([`ba9dec0`](https://github.com/IBM/compliance-trestle/commit/ba9dec0f4799b68160bd0e2aee66423763df21a6))
* Csv to oscal cd reconcile3 ([#1272](https://github.com/IBM/compliance-trestle/issues/1272)) ([`a19e7be`](https://github.com/IBM/compliance-trestle/commit/a19e7be1ce8b8fb267bfd797ddcad742fdf4fcfd))
* SSP cli changes to load comp defs ([#1264](https://github.com/IBM/compliance-trestle/issues/1264)) ([`2835eed`](https://github.com/IBM/compliance-trestle/commit/2835eed4bf700ca0f90120063a707fb811f610fb))
* Ssp based on components and refactor ([#1261](https://github.com/IBM/compliance-trestle/issues/1261)) ([`f0de73a`](https://github.com/IBM/compliance-trestle/commit/f0de73ad2152be75f456ff5a1b273d6c1d21988b))
* Create separate markdown directories per source ([#1242](https://github.com/IBM/compliance-trestle/issues/1242)) ([`3ffbdb0`](https://github.com/IBM/compliance-trestle/commit/3ffbdb04da1c72aba7b1304c0060d948d5501608))
* Add force-overwrite for generate ([#1241](https://github.com/IBM/compliance-trestle/issues/1241)) ([`d7612a9`](https://github.com/IBM/compliance-trestle/commit/d7612a9a769d72e7a0338506aed4013b299519a7))

### Fix
* BREAKING CHANGE ([#1311](https://github.com/IBM/compliance-trestle/issues/1311)) ([`cb86284`](https://github.com/IBM/compliance-trestle/commit/cb86284f1d6ee0299dc41d7d0fe66bb61139ce5a))
* Codeql update from v1 to v2 ([#1310](https://github.com/IBM/compliance-trestle/issues/1310)) ([`6731560`](https://github.com/IBM/compliance-trestle/commit/6731560201a596a986906086bf1d337d5495a816))
* Give warnings when component references control not loaded by profile for comp-gen and ssp-gen ([#1305](https://github.com/IBM/compliance-trestle/issues/1305)) ([`429b3c1`](https://github.com/IBM/compliance-trestle/commit/429b3c19023f4232b0853818c6039629dce4dc26))
* Temporary fix for the multiline control statement in catalog-assemble ([#1308](https://github.com/IBM/compliance-trestle/issues/1308)) ([`7a7aa8c`](https://github.com/IBM/compliance-trestle/commit/7a7aa8cf53c8361d79cc837615bbf7fae3b134c9))
* Boost test coverage for component generate and assemble ([#1306](https://github.com/IBM/compliance-trestle/issues/1306)) ([`52b863b`](https://github.com/IBM/compliance-trestle/commit/52b863b2ea684073afdb2ca85af7114ad43ac51c))
* Ssp-generate error with components ([#1303](https://github.com/IBM/compliance-trestle/issues/1303)) ([`7a49a0a`](https://github.com/IBM/compliance-trestle/commit/7a49a0a5e4a273755a2f6279a1cb51000cf02d40))
* Adding multiple value set to rule param values during component … ([#1301](https://github.com/IBM/compliance-trestle/issues/1301)) ([`c357e15`](https://github.com/IBM/compliance-trestle/commit/c357e15691bb9eee553c8531edd1f4ce024f60a3))
* Change python badge for addressing current python supported versions ([#1300](https://github.com/IBM/compliance-trestle/issues/1300)) ([`7a8d895`](https://github.com/IBM/compliance-trestle/commit/7a8d895d5ca16e9c7ebbcf3c862c14721d4a6421))
* Allow edit of rule param values during component assemble ([#1299](https://github.com/IBM/compliance-trestle/issues/1299)) ([`041a2c3`](https://github.com/IBM/compliance-trestle/commit/041a2c3d567b91404a7bc63ebdb9689b8a447463))
* Adding new components via markdown caused error ([#1294](https://github.com/IBM/compliance-trestle/issues/1294)) ([`39fd590`](https://github.com/IBM/compliance-trestle/commit/39fd590c85b7e2cf9b0e7770596def8c41e8ae98))
* Problem in cat assemble with subgroups ([#1291](https://github.com/IBM/compliance-trestle/issues/1291)) ([`88337a4`](https://github.com/IBM/compliance-trestle/commit/88337a4b16a24c8391a60e99347aa34cdb65307f))
* Assignment representation for ssp was not doing the right things ([#1273](https://github.com/IBM/compliance-trestle/issues/1273)) ([`cac2aa3`](https://github.com/IBM/compliance-trestle/commit/cac2aa351530f76834d53d10e08252ffb0786327))
* Remove attrs version pinning ([#1280](https://github.com/IBM/compliance-trestle/issues/1280)) ([`8260e03`](https://github.com/IBM/compliance-trestle/commit/8260e03cddcf682ebdf931f2b262f58156c8f56c))
* Fix typo in the curl ([#1278](https://github.com/IBM/compliance-trestle/issues/1278)) ([`d7576d5`](https://github.com/IBM/compliance-trestle/commit/d7576d5cc4e8536b1f94ca668b3b7b87e01f3148))
* Rules at component level2 ([#1259](https://github.com/IBM/compliance-trestle/issues/1259)) ([`3633d1f`](https://github.com/IBM/compliance-trestle/commit/3633d1f0f4bcd7ee481f7db382aab2b23e91687f))
* Trestle task csv-to-oscal-cd cannot handle whitespace ([#1252](https://github.com/IBM/compliance-trestle/issues/1252)) ([`ac4b5e0`](https://github.com/IBM/compliance-trestle/commit/ac4b5e08a8233d7f807cd6824197dca45f12b17b))
* Fix docs template validate flags ([#1245](https://github.com/IBM/compliance-trestle/issues/1245)) ([`6eac0c2`](https://github.com/IBM/compliance-trestle/commit/6eac0c2c620d933761e9660021a5005490bf5ea5))
* Adjust documentation ([#1248](https://github.com/IBM/compliance-trestle/issues/1248)) ([`5b31925`](https://github.com/IBM/compliance-trestle/commit/5b31925ac82042db98467552bfef415796ca57d3))
* Update flake8 in precommit ([#1246](https://github.com/IBM/compliance-trestle/issues/1246)) ([`a63b094`](https://github.com/IBM/compliance-trestle/commit/a63b094ef05924ba8a8a600ff7ec5192bfe285d8))

### Breaking
* Breaking release of Trestle ([`cb86284`](https://github.com/IBM/compliance-trestle/commit/cb86284f1d6ee0299dc41d7d0fe66bb61139ce5a))

### Documentation
* Update maintainers.md for missed contributors ([#1304](https://github.com/IBM/compliance-trestle/issues/1304)) ([`5443597`](https://github.com/IBM/compliance-trestle/commit/5443597b0b4cd826b58320e787f47d59f84fe06b))
* Change trestle project references to workspace ([#1276](https://github.com/IBM/compliance-trestle/issues/1276)) ([`2f1b4fd`](https://github.com/IBM/compliance-trestle/commit/2f1b4fd79bb67c509ee7f7c4f0d3a14502d0c71f))
* Create tutorial for task csv-to-cd (2) ([#1257](https://github.com/IBM/compliance-trestle/issues/1257)) ([`d31df9f`](https://github.com/IBM/compliance-trestle/commit/d31df9fb3ac4049f4710c2c9655ef8b1d17575e8))

## v1.2.0 (2022-11-07)
### Feature
* Allow trestle init to specify the purpose of initialisation ([#1228](https://github.com/IBM/compliance-trestle/issues/1228)) ([`8d02b68`](https://github.com/IBM/compliance-trestle/commit/8d02b68d5cae32273e179494bafb235c2a004a22))
* Provide full path to controls in catalog including sub-controls ([#1227](https://github.com/IBM/compliance-trestle/issues/1227)) ([`ec96ee9`](https://github.com/IBM/compliance-trestle/commit/ec96ee9067629b4d9932b39b2915b1b45bc6bae0))
* Get statement parts to allow easy capture of statement prose ([#1221](https://github.com/IBM/compliance-trestle/issues/1221)) ([`708b6b5`](https://github.com/IBM/compliance-trestle/commit/708b6b52e152ac4b21563f415cc0da3c8ca2ff8a))
* Remove default namespace and define generic trestle ns ([#1215](https://github.com/IBM/compliance-trestle/issues/1215)) ([`105152b`](https://github.com/IBM/compliance-trestle/commit/105152b15bab526429394ba398c3f512266086df))
* Made model equivalence check more rigorous ([#1217](https://github.com/IBM/compliance-trestle/issues/1217)) ([`ab89b45`](https://github.com/IBM/compliance-trestle/commit/ab89b45286dfbbfd1b3f4b9dc003246b4050b9e1))
* Allow profile-resolve to specify brackets around value ([#1207](https://github.com/IBM/compliance-trestle/issues/1207)) ([`16d9dbc`](https://github.com/IBM/compliance-trestle/commit/16d9dbcdc7fadaf7ddbbdd9c19b68e99777c4551))
* Show inherited props in yaml header for profile-generate markdown ([#1198](https://github.com/IBM/compliance-trestle/issues/1198)) ([`d4b4680`](https://github.com/IBM/compliance-trestle/commit/d4b4680e49ca8912ef34f0d472dc9997303227b8))
* Csv to oscal component definition ([#1197](https://github.com/IBM/compliance-trestle/issues/1197)) ([`c6e8bad`](https://github.com/IBM/compliance-trestle/commit/c6e8bad9f8c3feaab12778c90dde45830ab6ab01))
* Profile-resolve command to generate resolved profile catalog ([#1194](https://github.com/IBM/compliance-trestle/issues/1194)) ([`9faf572`](https://github.com/IBM/compliance-trestle/commit/9faf5726a1bc1bf8c9263a4d84a472653e76ebf9))
* Added new parameter rep ASSIGNMENT_FORM to leave params in brackets with text ([#1193](https://github.com/IBM/compliance-trestle/issues/1193)) ([`d41b2b6`](https://github.com/IBM/compliance-trestle/commit/d41b2b665b6e455288724347165f51b3078ac487))
* Allow culling headers from an existing md file ([#1180](https://github.com/IBM/compliance-trestle/issues/1180)) ([`a0a0369`](https://github.com/IBM/compliance-trestle/commit/a0a0369c53a7c06225e7e927aac8d8397f7b7c55))
* Handle display name and namespace ([#1165](https://github.com/IBM/compliance-trestle/issues/1165)) ([`a898216`](https://github.com/IBM/compliance-trestle/commit/a898216c812411646e263482393fd9669f43a5b2))
* Handle display name as property and initial handling of namespace option ([#1162](https://github.com/IBM/compliance-trestle/issues/1162)) ([`e6641fe`](https://github.com/IBM/compliance-trestle/commit/e6641fea53e486d41df899f5adc73ee6d79c8e8c))
* Profile add props to control or part, and add prose to statement part ([#1158](https://github.com/IBM/compliance-trestle/issues/1158)) ([`541eddb`](https://github.com/IBM/compliance-trestle/commit/541eddbfcbdf7b5fff6c4e6f765fda1a2f05bacf))
* Add various docs md improvements ([#1159](https://github.com/IBM/compliance-trestle/issues/1159)) ([`c93b4a1`](https://github.com/IBM/compliance-trestle/commit/c93b4a1554697d184544634fc182bdc01cfe5790))
* Add component-generate and component-assemble ([#1145](https://github.com/IBM/compliance-trestle/issues/1145)) ([`a4caab2`](https://github.com/IBM/compliance-trestle/commit/a4caab28c26b6391d4b258457c3009e960465a0f))

### Fix
* Use python 3.8 for the release ([#1236](https://github.com/IBM/compliance-trestle/issues/1236)) ([`7a9fbe8`](https://github.com/IBM/compliance-trestle/commit/7a9fbe8a1dba77357fd5b87136a56d9ad06bd3a0))
* Update the docs for governed documents ([#1219](https://github.com/IBM/compliance-trestle/issues/1219)) ([`b38a809`](https://github.com/IBM/compliance-trestle/commit/b38a809c95d04c269498c036df5bc1c198ab679e))
* Fix a bug in governed section validation ([#1231](https://github.com/IBM/compliance-trestle/issues/1231)) ([`c7f3c0d`](https://github.com/IBM/compliance-trestle/commit/c7f3c0d566c988c63979a3bfb40d351824898e3b))
* Add top level to parts output by get_statement_parts ([#1230](https://github.com/IBM/compliance-trestle/issues/1230)) ([`597999e`](https://github.com/IBM/compliance-trestle/commit/597999ef1898d5746e10b2fe706da7e4e57e936d))
* Change implementation prompt for part ([#1229](https://github.com/IBM/compliance-trestle/issues/1229)) ([`f929aba`](https://github.com/IBM/compliance-trestle/commit/f929abab713612810434363f8fc8530553b4b51a))
* Empty dirs were created during comp-gen ([#1225](https://github.com/IBM/compliance-trestle/issues/1225)) ([`805c9f3`](https://github.com/IBM/compliance-trestle/commit/805c9f3eb4b7cbd2ec717ae0cb0bec5cb0a2d37b))
* Issue #1222 ([#1223](https://github.com/IBM/compliance-trestle/issues/1223)) ([`96c7290`](https://github.com/IBM/compliance-trestle/commit/96c72902b6b4411e21df658cef5119f7be486829))
* Better handling of params in component generate ([#1220](https://github.com/IBM/compliance-trestle/issues/1220)) ([`2675e2f`](https://github.com/IBM/compliance-trestle/commit/2675e2f1ff5823787819b4854b4e35e034a1c8bf))
* Csv to oscal cd task ([#1208](https://github.com/IBM/compliance-trestle/issues/1208)) ([`049ee83`](https://github.com/IBM/compliance-trestle/commit/049ee83f70e955fa92817222405adbc08f8deb5e))
* Simple fix for statement labels not showing properly ([#1213](https://github.com/IBM/compliance-trestle/issues/1213)) ([`8d8ae1e`](https://github.com/IBM/compliance-trestle/commit/8d8ae1e5d388e2491e6558f1325ff4d22cc5a58d))
* Add profile title to comp-generate md and remove profile option ([#1202](https://github.com/IBM/compliance-trestle/issues/1202)) ([`711597b`](https://github.com/IBM/compliance-trestle/commit/711597b08490bcc8887d5970e376dc4c0e176df8))
* Component definition issues ([#1200](https://github.com/IBM/compliance-trestle/issues/1200)) ([`067fb91`](https://github.com/IBM/compliance-trestle/commit/067fb9171b8396515cfb2dc6b06623a65cf81183))
* Prof resolve should use moustache form as default ([#1196](https://github.com/IBM/compliance-trestle/issues/1196)) ([`530e28b`](https://github.com/IBM/compliance-trestle/commit/530e28bf2143427b9b9dc1aa3cbfb4fb5c3ef2aa))
* Profile assemble 'after' and 'by-id' issue, and added resolve_profile_catalog script ([#1190](https://github.com/IBM/compliance-trestle/issues/1190)) ([`4c772dc`](https://github.com/IBM/compliance-trestle/commit/4c772dcf141b9ffd6c92c62fb7efa586f82bd272))
* Pull display name from the resolved catalog ([#1192](https://github.com/IBM/compliance-trestle/issues/1192)) ([`8cedd9f`](https://github.com/IBM/compliance-trestle/commit/8cedd9f6ee4b45b8db762a81c2e59dfc83ce3504))
* Ssp-assemble was not capturing prose properly for control level imp req responses ([#1191](https://github.com/IBM/compliance-trestle/issues/1191)) ([`2a973cb`](https://github.com/IBM/compliance-trestle/commit/2a973cb83ebaf925071c3bb59c0205b6e0387da3))
* Name of subparts added into statement should not be "item" ([#1184](https://github.com/IBM/compliance-trestle/issues/1184)) ([`fcc79cb`](https://github.com/IBM/compliance-trestle/commit/fcc79cb7db14385db1e2e174f27d18726ae4392e))
* Add subparts to the markdown docs ([#1182](https://github.com/IBM/compliance-trestle/issues/1182)) ([`44e286b`](https://github.com/IBM/compliance-trestle/commit/44e286ba1ba7369607b4299a13600c117fafd5ca))
* Parts labeled Control should be Part ([#1176](https://github.com/IBM/compliance-trestle/issues/1176)) ([`6287991`](https://github.com/IBM/compliance-trestle/commit/62879916da55804bd7171ba51c6794ec021e36d5))
* Fix various issues in markdown docs ([#1174](https://github.com/IBM/compliance-trestle/issues/1174)) ([`4615be2`](https://github.com/IBM/compliance-trestle/commit/4615be22ba4522455c441b8474aac45042606024))
* Prevent output of default namespace in markdown ([#1173](https://github.com/IBM/compliance-trestle/issues/1173)) ([`7ffc37e`](https://github.com/IBM/compliance-trestle/commit/7ffc37e0f0ef67c9a30bb309a7cf7eee11a77c24))
* Combine parts props into a single add rather than two separate ones ([#1172](https://github.com/IBM/compliance-trestle/issues/1172)) ([`a1ded2c`](https://github.com/IBM/compliance-trestle/commit/a1ded2c08bb94c9b5b61ef828ac6fc73a3fb00c4))
* Only show missing value warnings when resolving a profile for ssp ([#1171](https://github.com/IBM/compliance-trestle/issues/1171)) ([`4afb7fc`](https://github.com/IBM/compliance-trestle/commit/4afb7fc5b2cbb750bd4dbdd99e61825c04b61c07))
* Duplicate headers and statement parts added in wrong place ([#1163](https://github.com/IBM/compliance-trestle/issues/1163)) ([`ee505f5`](https://github.com/IBM/compliance-trestle/commit/ee505f5b14a0281e9bda1365de7a4f2b15a5096b))
* Utf8 issue ([#1160](https://github.com/IBM/compliance-trestle/issues/1160)) ([`f1e2a9f`](https://github.com/IBM/compliance-trestle/commit/f1e2a9fa0f44db46fd6674be29cbf1b7dd5bf14e))
* Fix global headers validation when no drawio files are present ([#1155](https://github.com/IBM/compliance-trestle/issues/1155)) ([`0d59427`](https://github.com/IBM/compliance-trestle/commit/0d59427b89d3303b1392c08a7aa07a4ccdcab8a1))
* Component generate with new format, clean up of cache tests ([#1153](https://github.com/IBM/compliance-trestle/issues/1153)) ([`a5ab848`](https://github.com/IBM/compliance-trestle/commit/a5ab848e836198b09fe819307a2931de072df400))
* Handle adding/deleting section from the markdown control ([#1154](https://github.com/IBM/compliance-trestle/issues/1154)) ([`40cd08b`](https://github.com/IBM/compliance-trestle/commit/40cd08ba48522d20b26343690fb43f57580c610b))
* Bump mkdocstring version ([#1151](https://github.com/IBM/compliance-trestle/issues/1151)) ([`aad593b`](https://github.com/IBM/compliance-trestle/commit/aad593b7fdf0a7019c736d5e464a7136f76f5085))
* Correct typo in README ([#1142](https://github.com/IBM/compliance-trestle/issues/1142)) ([`160707a`](https://github.com/IBM/compliance-trestle/commit/160707a2e2fc23879085263806e851584d2dd405))
* Dont add empty template folder ([#1140](https://github.com/IBM/compliance-trestle/issues/1140)) ([`cf7a63b`](https://github.com/IBM/compliance-trestle/commit/cf7a63bea9b442d39af8f4dccda5f7d484314cf6))
* Allow catalog groups with no id and fix validation of links and reference matching ([#1137](https://github.com/IBM/compliance-trestle/issues/1137)) ([`9e1b206`](https://github.com/IBM/compliance-trestle/commit/9e1b20686b85d166cee98b444e8deb7f40c06b3e))
* Catalog-assemble was writing a new file when there were no changes to the file ([#1139](https://github.com/IBM/compliance-trestle/issues/1139)) ([`e6949e2`](https://github.com/IBM/compliance-trestle/commit/e6949e276dd683f5f54072b7db29c9bf15335d34))
* Remove extraneous parens in unit tests. ([#1138](https://github.com/IBM/compliance-trestle/issues/1138)) ([`90cb2ee`](https://github.com/IBM/compliance-trestle/commit/90cb2ee8f3d6b04c69971a542440ad66fec5188c))
* Fix trestle version in the docs ([#1134](https://github.com/IBM/compliance-trestle/issues/1134)) ([`d7d3cfc`](https://github.com/IBM/compliance-trestle/commit/d7d3cfce8f2de248fc957a5146907cac118071a6))
* Improve logging when validating headings in gov docs ([#1133](https://github.com/IBM/compliance-trestle/issues/1133)) ([`a641299`](https://github.com/IBM/compliance-trestle/commit/a6412996d991c49261448b6eae80471d37ab2664))

### Documentation
* Update ssp and profile authoring guide to describe addition of parts ([#1185](https://github.com/IBM/compliance-trestle/issues/1185)) ([`35c3c78`](https://github.com/IBM/compliance-trestle/commit/35c3c78105721712340a3ab1a9fbe3fdba44ac8e))

## v1.1.0 (2022-05-24)
### Feature
* Filter ssp by component ([`d675e49`](https://github.com/IBM/compliance-trestle/commit/d675e4936151d0467362ada4442154cb841d87e2))
* Validate refs and resources in catalogs and models ([`1c17bf7`](https://github.com/IBM/compliance-trestle/commit/1c17bf75df4ceab99c6f3ae68ee620e57738d592))

### Fix
* Resolve pre-commit issue ([#1126](https://github.com/IBM/compliance-trestle/issues/1126)) ([`679cadc`](https://github.com/IBM/compliance-trestle/commit/679cadc8bb839131d7a458b4b5cd082ed4535e24))
* Do not validate extra files in author folders ([`25a1721`](https://github.com/IBM/compliance-trestle/commit/25a172160c651411c1521507557450d49592561d))
* Better handling of child controls ([`c224f92`](https://github.com/IBM/compliance-trestle/commit/c224f929ce2f9e682149e73055b7b195bbdaf92c))
* Remove unused classes from the generated oscal files ([`9a3ee20`](https://github.com/IBM/compliance-trestle/commit/9a3ee20be9520bad084ac2df556eacbd23c7907f))
* Allow subfolders in template folder ([`7223e1b`](https://github.com/IBM/compliance-trestle/commit/7223e1b7d9dd8ef659867853a00cdbc7ca66a050))
* Updated documentation ([`8eca1f0`](https://github.com/IBM/compliance-trestle/commit/8eca1f0abc4a62a6e1db34b32b4f615aff097c0d))
* Add control id to the generated docs ([`b666956`](https://github.com/IBM/compliance-trestle/commit/b666956adf221420b77a980eedec2ffc044d0e6e))

## v1.0.2 (2022-05-05)
### Fix
* Check for circular imports during profile resolution ([#1107](https://github.com/IBM/compliance-trestle/issues/1107)) ([`81469db`](https://github.com/IBM/compliance-trestle/commit/81469dbcca3ffcb140ac09023b7de17671c4386b))
* Prevent moustaches in resolved profile catalog ([#1106](https://github.com/IBM/compliance-trestle/issues/1106)) ([`f9edc81`](https://github.com/IBM/compliance-trestle/commit/f9edc8185db30330cfe33d3cf02ef55e90135692))
* Add ability to remove group title ([#1114](https://github.com/IBM/compliance-trestle/issues/1114)) ([`4303d76`](https://github.com/IBM/compliance-trestle/commit/4303d760935b0f34a13cccf9caaac4e90a05de83))
* Prevent blowfish warning due to new release of cryptography ([#1112](https://github.com/IBM/compliance-trestle/issues/1112)) ([`f13fe31`](https://github.com/IBM/compliance-trestle/commit/f13fe31ae4c790ef7b495c3f5418d3c26de96841))

## v1.0.1 (2022-04-27)
### Fix
* Bump readme refs to 1.0.x ([#1103](https://github.com/IBM/compliance-trestle/issues/1103)) ([`488cd40`](https://github.com/IBM/compliance-trestle/commit/488cd4003a97d0142cc65e91fa660dd2b83bd75b))

## v1.0.0 (2022-04-27)
### Feature
* Updated to OSCAL 1.0.2 support ([#1097](https://github.com/IBM/compliance-trestle/issues/1097)) ([`a2aa3dd`](https://github.com/IBM/compliance-trestle/commit/a2aa3dd53e67096004ba4e202fef8c7586462888))

### Fix
* Various task transformer improvements ([#1100](https://github.com/IBM/compliance-trestle/issues/1100)) ([`c869f37`](https://github.com/IBM/compliance-trestle/commit/c869f37f9c942dc151ac729a6fa3506c375c9da7))

### Breaking
* pushed to OSCAL 1.0.2 ([`a2aa3dd`](https://github.com/IBM/compliance-trestle/commit/a2aa3dd53e67096004ba4e202fef8c7586462888))

### Documentation
* Update readme and index md files ([#1099](https://github.com/IBM/compliance-trestle/issues/1099)) ([`f0bd541`](https://github.com/IBM/compliance-trestle/commit/f0bd5412be6bb7b9f88dc2ee3f6b1608c12a9268))

## v0.37.0 (2022-04-12)
### Feature
* Bump feature with added docs ([#1092](https://github.com/IBM/compliance-trestle/issues/1092)) ([`d1cdad3`](https://github.com/IBM/compliance-trestle/commit/d1cdad3360a122cfa9bcd7ea8c3252369966f49e))

### Fix
* Cherry pick all fixes from the prerelease hotfix branch ([#1090](https://github.com/IBM/compliance-trestle/issues/1090)) ([`06e1470`](https://github.com/IBM/compliance-trestle/commit/06e147088ec0808bd04f7a5f4a10dc1f13bb7275))
* Improved filtering column matching. ([#1082](https://github.com/IBM/compliance-trestle/issues/1082)) ([`712822e`](https://github.com/IBM/compliance-trestle/commit/712822e387c592f667a763ede6f145590a9b088e))

### Documentation
* Small fixes to cli.md ([#1091](https://github.com/IBM/compliance-trestle/issues/1091)) ([`6206869`](https://github.com/IBM/compliance-trestle/commit/6206869f12a16150fccb652896c1743add1a8c59))

## v0.36.0 (2022-04-04)
### Feature
* Add ability to generate multiple markdown files using Jinja ([#1077](https://github.com/IBM/compliance-trestle/issues/1077)) ([`f41fc9f`](https://github.com/IBM/compliance-trestle/commit/f41fc9fe3df95985f50ef29e09be07962fc8a7e9))

### Fix
* Profile tools now handle choice and label properly ([#1078](https://github.com/IBM/compliance-trestle/issues/1078)) ([`4d9363a`](https://github.com/IBM/compliance-trestle/commit/4d9363ab827cc3d26a032336b35a50feec9a59ad))
* Jinja control loops sort controls better ([#1076](https://github.com/IBM/compliance-trestle/issues/1076)) ([`d89128b`](https://github.com/IBM/compliance-trestle/commit/d89128b83deddcd64dfab00d0a7ddcabe8415349))
* Catalog name confusion and overwrite of same assembled files ([#1074](https://github.com/IBM/compliance-trestle/issues/1074)) ([`1ba9a35`](https://github.com/IBM/compliance-trestle/commit/1ba9a35dee356e3b8df0fedbad30d9a420fa4e79))
* Trestle transformation tasks naming convention. ([#1071](https://github.com/IBM/compliance-trestle/issues/1071)) ([`d179d78`](https://github.com/IBM/compliance-trestle/commit/d179d78671f2926c1651ad1eaa8f906f8c2aaefb))
* Delay choice subst ([#1072](https://github.com/IBM/compliance-trestle/issues/1072)) ([`16cf5e4`](https://github.com/IBM/compliance-trestle/commit/16cf5e4374ce5f304cd491d1dc1e30de07e6a293))
* Param choice substitution works properly ([#1070](https://github.com/IBM/compliance-trestle/issues/1070)) ([`181f586`](https://github.com/IBM/compliance-trestle/commit/181f58697ef18b114dd339e0ac903ee52bfa6c97))
* Use set-parms of CD ctl-impl for alternatives; discard catalog hack ([#1068](https://github.com/IBM/compliance-trestle/issues/1068)) ([`d9e75e7`](https://github.com/IBM/compliance-trestle/commit/d9e75e78b53851232adc635eca4f224e4c05d81a))
* Fix Jinja dependency version ([#1069](https://github.com/IBM/compliance-trestle/issues/1069)) ([`34c703a`](https://github.com/IBM/compliance-trestle/commit/34c703abca210c9e2c2d4675822119214f1bf3e5))
* Added methods in catalog interface to sort controls by sort-id ([#1067](https://github.com/IBM/compliance-trestle/issues/1067)) ([`dd04292`](https://github.com/IBM/compliance-trestle/commit/dd04292d41090fb951b5a6284356e41c6a07d62a))
* Lock oscal to release-1.0.0 ([#1065](https://github.com/IBM/compliance-trestle/issues/1065)) ([`1e6b554`](https://github.com/IBM/compliance-trestle/commit/1e6b5547ed53b82e45f0c9478cc91970c8980d29))

### Documentation
* Update ssp and profile authoring document ([#1075](https://github.com/IBM/compliance-trestle/issues/1075)) ([`4211529`](https://github.com/IBM/compliance-trestle/commit/42115298bb835885eb6662d8dabfcd68e05b1f59))

## v0.35.0 (2022-03-22)
### Feature
* Xlsx filter ([#1050](https://github.com/IBM/compliance-trestle/issues/1050)) ([`9f63412`](https://github.com/IBM/compliance-trestle/commit/9f6341257f755e49173050b4d0f2e32c75874610))
* Xlsx-to-oscal-profile ([#1046](https://github.com/IBM/compliance-trestle/issues/1046)) ([`9695933`](https://github.com/IBM/compliance-trestle/commit/96959339818baaa06b0a9c00dedae81c9c99dcec))
* Resolve UUID Imports During Profile Resolution, Not Only Explicit Imports ([#1023](https://github.com/IBM/compliance-trestle/issues/1023)) ([`ae803e7`](https://github.com/IBM/compliance-trestle/commit/ae803e74cda58694a294ccfe1e979f2993626ec8))
* Aggregate properties as results level ([#997](https://github.com/IBM/compliance-trestle/issues/997)) ([`174aabe`](https://github.com/IBM/compliance-trestle/commit/174aabe401b9fbe35a10efcc9df159a3537d3c0d))
* Validate OSCAL directories ([#990](https://github.com/IBM/compliance-trestle/issues/990)) ([`941e4fc`](https://github.com/IBM/compliance-trestle/commit/941e4fc6fe9e3c4700f4f7c43be849fb176fb57d))

### Fix
* Use control sort-id for sorting ([#1062](https://github.com/IBM/compliance-trestle/issues/1062)) ([`fb65bfb`](https://github.com/IBM/compliance-trestle/commit/fb65bfbaadca2240f535d7db057baed108ec0bf2))
* Task tanium-to-oscal poor aggregation performance ([#1053](https://github.com/IBM/compliance-trestle/issues/1053)) ([`9ea118c`](https://github.com/IBM/compliance-trestle/commit/9ea118c472b83491a30bbeabe35afbc35fd4e96d))
* Avoid write of new file if no changes after -assemble ([#1057](https://github.com/IBM/compliance-trestle/issues/1057)) ([`893eec6`](https://github.com/IBM/compliance-trestle/commit/893eec6afcf6eaaa9f831528995de267a0cabe6b))
* Update timestamps for all assemble tools ([#1056](https://github.com/IBM/compliance-trestle/issues/1056)) ([`cccd7a2`](https://github.com/IBM/compliance-trestle/commit/cccd7a2e9399bf001ab101a405f370d92c1d000c))
* Flake8 bandit reenable, remove transformcmd, empty config.ini ([#1055](https://github.com/IBM/compliance-trestle/issues/1055)) ([`a7543c2`](https://github.com/IBM/compliance-trestle/commit/a7543c24c80b6904a27a678aff3bce357fc44629))
* More complete parameter info in yaml headers ([#1049](https://github.com/IBM/compliance-trestle/issues/1049)) ([`7a3b098`](https://github.com/IBM/compliance-trestle/commit/7a3b098d2ef9f88f564908927240524021d5c768))
* Block withdrawn controls from being written as markdown ([#1045](https://github.com/IBM/compliance-trestle/issues/1045)) ([`053ab0e`](https://github.com/IBM/compliance-trestle/commit/053ab0eac098104ed062acb80b4b65f419d37323))
* Remove add command and incorporate it into the create command ([#1036](https://github.com/IBM/compliance-trestle/issues/1036)) ([`ddde5f5`](https://github.com/IBM/compliance-trestle/commit/ddde5f537158f5621f3d5d0a06791400076d4a4f))
* Improve column heading matching. ([#1035](https://github.com/IBM/compliance-trestle/issues/1035)) ([`a51fa1e`](https://github.com/IBM/compliance-trestle/commit/a51fa1e9a953dd84e88c344b4d8368d90e9cea41))
* Improve sections ([#1033](https://github.com/IBM/compliance-trestle/issues/1033)) ([`8e6c632`](https://github.com/IBM/compliance-trestle/commit/8e6c632237747e6e75cf24886418438a25ae46f1))
* Consistent author commands and support for required-sections ([#1030](https://github.com/IBM/compliance-trestle/issues/1030)) ([`08953d1`](https://github.com/IBM/compliance-trestle/commit/08953d19a2144f98051b33917eca534521de115c))
* Profile params ([#1015](https://github.com/IBM/compliance-trestle/issues/1015)) ([`30c0ec1`](https://github.com/IBM/compliance-trestle/commit/30c0ec1097140c9e88bc43f46a2ccc7a1273f81e))
* 2 bugs xlsx-to-oscal-component-definition ([#1017](https://github.com/IBM/compliance-trestle/issues/1017)) ([`81d4bf2`](https://github.com/IBM/compliance-trestle/commit/81d4bf2682dacaba3ee09061a790e8a2c15564a4))
* Updated documentation for trestle ([#1006](https://github.com/IBM/compliance-trestle/issues/1006)) ([`8d3187d`](https://github.com/IBM/compliance-trestle/commit/8d3187dd27cbf2fec0eab787bf6b19ddceebf519))
* Missing params in generated catalog and better hidden file handling on windows ([#999](https://github.com/IBM/compliance-trestle/issues/999)) ([`c4550f5`](https://github.com/IBM/compliance-trestle/commit/c4550f541c53327bac3ad38f1feaf262d0b9be27))
* Second stage code cleanup and dead code removal ([#993](https://github.com/IBM/compliance-trestle/issues/993)) ([`79b2f61`](https://github.com/IBM/compliance-trestle/commit/79b2f61baac7adbf69e1474a5e218d664bec65ff))
* Cleanup phase I including split of profile_resolver ([#991](https://github.com/IBM/compliance-trestle/issues/991)) ([`39134aa`](https://github.com/IBM/compliance-trestle/commit/39134aad2ee55e60a89f59c691dc145008b77206))
* Allow trace logging with verbose level 2 ([#989](https://github.com/IBM/compliance-trestle/issues/989)) ([`7b4b349`](https://github.com/IBM/compliance-trestle/commit/7b4b34955020ff5f2608c0f9af84520f45cb86f7))
* README documentation improvements ([#987](https://github.com/IBM/compliance-trestle/issues/987)) ([`0ad4996`](https://github.com/IBM/compliance-trestle/commit/0ad499611c3fd6a0c0e8dc258bb1dd8190e4bfba))
* Change verbose assignments from boolean to integer ([#988](https://github.com/IBM/compliance-trestle/issues/988)) ([`6aed714`](https://github.com/IBM/compliance-trestle/commit/6aed7142334af6ee97345248224d05de875eae12))

### Documentation
* Ssp tutorial update ([#1034](https://github.com/IBM/compliance-trestle/issues/1034)) ([`12ab44f`](https://github.com/IBM/compliance-trestle/commit/12ab44f39a15f8de0388cf7ffab3cce44bc396cf))
* Fix typo personell->personnel. ([#1014](https://github.com/IBM/compliance-trestle/issues/1014)) ([`f3041be`](https://github.com/IBM/compliance-trestle/commit/f3041beea9ea6093bc7b462521c9cff325cf9f4b))

## v0.34.0 (2022-01-07)
### Feature
* Add custom parameter wrapping to jinja ([#976](https://github.com/IBM/compliance-trestle/issues/976)) ([`4289ca0`](https://github.com/IBM/compliance-trestle/commit/4289ca0bd1cac83146a4f9080e0eb7f766d78db3))
* Add jinja datestamp output ([#970](https://github.com/IBM/compliance-trestle/issues/970)) ([`2b92da1`](https://github.com/IBM/compliance-trestle/commit/2b92da100f0646dabf3a56a6544dd72bc66c4958))
* Add optional numbering of figures and tables when generating md… ([#964](https://github.com/IBM/compliance-trestle/issues/964)) ([`89bafe7`](https://github.com/IBM/compliance-trestle/commit/89bafe7f1fcfe3fe1db4900be483f8416fb824b7))

### Fix
* OCP4 CIS Component Definition rules should have unique descriptions ([#975](https://github.com/IBM/compliance-trestle/issues/975)) ([`299db5a`](https://github.com/IBM/compliance-trestle/commit/299db5acffe3f247cba86382a873cc1029b45ded))
* Better handling of groups containing groups in ssp gen and assemble ([#977](https://github.com/IBM/compliance-trestle/issues/977)) ([`5fa1820`](https://github.com/IBM/compliance-trestle/commit/5fa18203d89ff353f8500f892b85b957385ebb11))
* Several issues in profile assemble and catalog generate ([#974](https://github.com/IBM/compliance-trestle/issues/974)) ([`0435c84`](https://github.com/IBM/compliance-trestle/commit/0435c8405e4ff1b6608ec93fb3baafb61356d1d8))
* Fix json blocks in md so mdformat doesnt raise cannot format warning ([#973](https://github.com/IBM/compliance-trestle/issues/973)) ([`73b0612`](https://github.com/IBM/compliance-trestle/commit/73b061275e101c19e34a45fa5ab959b1f29f6293))
* Add toml as yapf pre-commit dependency ([#972](https://github.com/IBM/compliance-trestle/issues/972)) ([`d026282`](https://github.com/IBM/compliance-trestle/commit/d0262826f30e0c7f89f8a3551b93142669fa2c66))
* Fix blind link in readme ([#969](https://github.com/IBM/compliance-trestle/issues/969)) ([`3f054bd`](https://github.com/IBM/compliance-trestle/commit/3f054bd8d82032371955627023ceb257e2f3d4f6))
* Handle error when dealing with profiles with no modify object. ([#963](https://github.com/IBM/compliance-trestle/issues/963)) ([`7ad3c82`](https://github.com/IBM/compliance-trestle/commit/7ad3c82058991507808580e800f0bc9df16d2071))

### Documentation
* Update ssp workflow and minor changes to other docs ([#985](https://github.com/IBM/compliance-trestle/issues/985)) ([`45be184`](https://github.com/IBM/compliance-trestle/commit/45be1842d1fdc634d8ae9b5b404da4e59ea13d18))

## v0.33.0 (2021-12-21)
### Feature
* Support for SSP writing with jinja templating. ([#787](https://github.com/IBM/compliance-trestle/issues/787)) ([`e47fc77`](https://github.com/IBM/compliance-trestle/commit/e47fc778ab66a8997b689753ce5ead1849543e52))

### Fix
* Merge dicts and remove transform command from CLI until mature.(#954) ([`82e484b`](https://github.com/IBM/compliance-trestle/commit/82e484b59a4415c2ece1fda55b2b7e9f1a46ab68))

## v0.32.1 (2021-12-17)
### Fix
* Cidd issues ([#949](https://github.com/IBM/compliance-trestle/issues/949)) ([`038ca2e`](https://github.com/IBM/compliance-trestle/commit/038ca2ec96a6d85aa891d0cf36e9f9c03e0733d7))
* OSCO rules with prefix ocp- and dashes ([#932](https://github.com/IBM/compliance-trestle/issues/932)) ([`64f7a97`](https://github.com/IBM/compliance-trestle/commit/64f7a973f5bb7c7946b789770034da186dbcd77e))

## v0.32.0 (2021-12-14)
### Feature
* Added documentation for fedramp plugin ([#936](https://github.com/IBM/compliance-trestle/issues/936)) ([`3deff2c`](https://github.com/IBM/compliance-trestle/commit/3deff2c857c55348242e06a74f2647224517506c))
* Params in header for profile generate and assemble ([#935](https://github.com/IBM/compliance-trestle/issues/935)) ([`a1b293f`](https://github.com/IBM/compliance-trestle/commit/a1b293f8cac65d32b1cf21a22f49e02967f4e184))
* Tutorial cis-to-catalog ([#931](https://github.com/IBM/compliance-trestle/issues/931)) ([`e2842a8`](https://github.com/IBM/compliance-trestle/commit/e2842a8d66a261c98e973a7edf1bdddb2a342d06))
* Task cis-to-catalog ([#911](https://github.com/IBM/compliance-trestle/issues/911)) ([`0a492d0`](https://github.com/IBM/compliance-trestle/commit/0a492d01977467fb6839fbc83322149f5474bbe4))
* Roles in metadata ([#926](https://github.com/IBM/compliance-trestle/issues/926)) ([`ddc1e66`](https://github.com/IBM/compliance-trestle/commit/ddc1e662ef345eaecf5b5584964d5739f1c3ab43))
* Allow components in markdown and ssp assemble ([#902](https://github.com/IBM/compliance-trestle/issues/902)) ([`b03a236`](https://github.com/IBM/compliance-trestle/commit/b03a236ad2928b384677e5777b1880d3386a4fe0))
* Add ability to modify headers in the tree ([#909](https://github.com/IBM/compliance-trestle/issues/909)) ([`b455c18`](https://github.com/IBM/compliance-trestle/commit/b455c18c3492b7e4a4fced8b701780d109bed55e))
* Altering ssp-generate to add all sections by default ([#905](https://github.com/IBM/compliance-trestle/issues/905)) ([`55a399b`](https://github.com/IBM/compliance-trestle/commit/55a399bf129aa39e42e83e93e8b1b69aec20d9bb))

### Fix
* Fire off sonar only on local PRs. ([#934](https://github.com/IBM/compliance-trestle/issues/934)) ([`26f4f0a`](https://github.com/IBM/compliance-trestle/commit/26f4f0ab08af2d37c05130e3189bfa74f79b5a57))
* Ensuring that mkdocs yaml both remains stable an is up to date. ([#927](https://github.com/IBM/compliance-trestle/issues/927)) ([`ee48763`](https://github.com/IBM/compliance-trestle/commit/ee487634cbf80b3aeac12a7f103c19730b18e2da))

### Documentation
* Clear edit_uri to remove edit pencil ([#937](https://github.com/IBM/compliance-trestle/issues/937)) ([`e32c7ce`](https://github.com/IBM/compliance-trestle/commit/e32c7ce46df3ff905e115ab315c36005f8e0e246))
* Add versioning tutorial ([#917](https://github.com/IBM/compliance-trestle/issues/917)) ([`b682806`](https://github.com/IBM/compliance-trestle/commit/b682806f25783a8cc4df18647ac96973d365012d))

## v0.31.0 (2021-12-01)
### Feature
* Added trestle-fedramp project discovery and command ([#899](https://github.com/IBM/compliance-trestle/issues/899)) ([`f0cc836`](https://github.com/IBM/compliance-trestle/commit/f0cc8367a9001749a81c1a069f02ea00e49a7cec))
* Ignore files from the validation ([#898](https://github.com/IBM/compliance-trestle/issues/898)) ([`c2af814`](https://github.com/IBM/compliance-trestle/commit/c2af8148cd7698bc75803bec0c4d6b181e11cd64))
* Enforce OSCAL version and notify user ([#895](https://github.com/IBM/compliance-trestle/issues/895)) ([`246875c`](https://github.com/IBM/compliance-trestle/commit/246875ce0c7d42f931072739ae340b39bbb0399e))
* Sample generic oscal transform to filter ssp by profile ([#820](https://github.com/IBM/compliance-trestle/issues/820)) ([`afe243f`](https://github.com/IBM/compliance-trestle/commit/afe243f6ece6fb9b361870e69b32d8d84a2e9335))

### Fix
* Remove empty folders ([#904](https://github.com/IBM/compliance-trestle/issues/904)) ([`552fb36`](https://github.com/IBM/compliance-trestle/commit/552fb36a53198d9d1fcc06a0a3eb3cfe59b753b2))
* Tmp req init ([#894](https://github.com/IBM/compliance-trestle/issues/894)) ([`e2d3ed0`](https://github.com/IBM/compliance-trestle/commit/e2d3ed0f98a281ac5ef77edf5f4e90a0a09f53d8))
* Bad control causes uncaught exception in ssp-generate ([#893](https://github.com/IBM/compliance-trestle/issues/893)) ([`c50515a`](https://github.com/IBM/compliance-trestle/commit/c50515a55452b776ed9397b62e658fb5d5b1d5b0))
* Ignore subfolders in folders validation ([#889](https://github.com/IBM/compliance-trestle/issues/889)) ([`727265a`](https://github.com/IBM/compliance-trestle/commit/727265aebbcbdeffce5575c5907ba1fd000bdea3))

## v0.30.0 (2021-11-22)
### Feature
* OSCO transformer support for OpenScap 1.3.5 ([#876](https://github.com/IBM/compliance-trestle/issues/876)) ([`dcfb34a`](https://github.com/IBM/compliance-trestle/commit/dcfb34ae67ce0bf057d224a6eb4065e25d616a42))

## v0.29.0 (2021-11-19)
### Feature
* Tutorial for task cis-to-component-definition ([#870](https://github.com/IBM/compliance-trestle/issues/870)) ([`4e4d6b4`](https://github.com/IBM/compliance-trestle/commit/4e4d6b4ba600792ce5a6dfd3606fb730099cbdef))
* Add support for ignored fields to header ([#794](https://github.com/IBM/compliance-trestle/issues/794)) ([`37e9b60`](https://github.com/IBM/compliance-trestle/commit/37e9b60cecf6516c934fafa8fa969672ade8ef7f))

### Fix
* Cat assemble label needs to load labels as properties when reading controls ([#878](https://github.com/IBM/compliance-trestle/issues/878)) ([`0b97476`](https://github.com/IBM/compliance-trestle/commit/0b97476db8bfbac4925b2af2ec1b8edda9178e33))
* Cleanup PR template. ([`f7c433b`](https://github.com/IBM/compliance-trestle/commit/f7c433b8a4d86a39150e596e4e395b03a2dab984))
* Current support for multiple PR templates is insufficient in Github. ([#879](https://github.com/IBM/compliance-trestle/issues/879)) ([`bf12f2e`](https://github.com/IBM/compliance-trestle/commit/bf12f2e464adaf371ec2f7f63050395a05ec1cfb))
* Updating documentation to exploit code highlighting. ([#877](https://github.com/IBM/compliance-trestle/issues/877)) ([`10bd679`](https://github.com/IBM/compliance-trestle/commit/10bd6792d8a9b9b42d26653fffd40baaad4d3251))
* Mangled merging of lists and lack of recursion in profile resolver ([#869](https://github.com/IBM/compliance-trestle/issues/869)) ([`e3ccbbc`](https://github.com/IBM/compliance-trestle/commit/e3ccbbc4c6675264dcc245ed6c5e2454d04078c8))
* Incorrect behaviour of lint PR. ([#868](https://github.com/IBM/compliance-trestle/issues/868)) ([`e5209c3`](https://github.com/IBM/compliance-trestle/commit/e5209c33f8d53bd022e410d52ef97d3316746023))

## v0.28.1 (2021-11-17)
### Fix
* Remove results {} from osco-to-oscal console display ([#866](https://github.com/IBM/compliance-trestle/issues/866)) ([`d62051e`](https://github.com/IBM/compliance-trestle/commit/d62051e0fb45c99edd97b0314117b7208dd11d91))
* Add spec.desctiption to produced yaml ([#865](https://github.com/IBM/compliance-trestle/issues/865)) ([`b988684`](https://github.com/IBM/compliance-trestle/commit/b988684ffb02011c4f890b8f889abb0c7184e03c))

## v0.28.0 (2021-11-16)
### Feature
* Add yaml header to various trestle author docs in a safe manner. ([#853](https://github.com/IBM/compliance-trestle/issues/853)) ([`0b6f8a1`](https://github.com/IBM/compliance-trestle/commit/0b6f8a18d1de460c14fa36d107729e367682045e))

### Fix
* Fix instance version ([#862](https://github.com/IBM/compliance-trestle/issues/862)) ([`56f7cdf`](https://github.com/IBM/compliance-trestle/commit/56f7cdfe537adfcfcb8398df7d06b71cbf35781d))
* Correcting mkdocs ([#860](https://github.com/IBM/compliance-trestle/issues/860)) ([`89a6d0d`](https://github.com/IBM/compliance-trestle/commit/89a6d0dc42d87b7082ec4c1a2def684cc4ae543b))
* Relabel yaml-safe to header-dont-merge. ([#858](https://github.com/IBM/compliance-trestle/issues/858)) ([`58e6b1d`](https://github.com/IBM/compliance-trestle/commit/58e6b1d8bec4a5b210d47d24acaf2ea770a31000))
* 2 bugs in task cis-to-component-definition ([#856](https://github.com/IBM/compliance-trestle/issues/856)) ([`61da0b8`](https://github.com/IBM/compliance-trestle/commit/61da0b89aaab4c15b0e4a2c885efbdf387b30d10))
* Fix headers recurse flag ([#849](https://github.com/IBM/compliance-trestle/issues/849)) ([`d285cc6`](https://github.com/IBM/compliance-trestle/commit/d285cc61ff52531d821c03ab4bcfdf4966b9c44e))

## v0.27.2 (2021-11-16)
### Fix
* Force trestle relesae. ([`49243e3`](https://github.com/IBM/compliance-trestle/commit/49243e369120958536a644a4a063cf19f1870b7a))

## v0.27.1 (2021-11-15)
### Fix
* Profile resolver issues with alter that has no adds ([#847](https://github.com/IBM/compliance-trestle/issues/847)) ([`6865eb7`](https://github.com/IBM/compliance-trestle/commit/6865eb7967ae954b14f5a10921d88ca567fae921))

## v0.27.0 (2021-11-14)
### Feature
* Add ability to use different versions of templates ([#837](https://github.com/IBM/compliance-trestle/issues/837)) ([`c6d3618`](https://github.com/IBM/compliance-trestle/commit/c6d3618f13e6dc945413867a8d102cd3a7c3c211))
* Facilitate improved performance within Tanium transformer. ([#835](https://github.com/IBM/compliance-trestle/issues/835)) ([`4d2ded4`](https://github.com/IBM/compliance-trestle/commit/4d2ded49d314f6e632f531b08a58bc66d53d8997))
* Significant json (de)serialisation performance improvements. ([#841](https://github.com/IBM/compliance-trestle/issues/841)) ([`d6f3cb1`](https://github.com/IBM/compliance-trestle/commit/d6f3cb1ab8113c997d463d832aa8c8b721faffd2))
* Add yaml header output for profile and catalog generate ([#833](https://github.com/IBM/compliance-trestle/issues/833)) ([`50093f0`](https://github.com/IBM/compliance-trestle/commit/50093f075615fe25bb6e25b16ff5d98fb0a308f9))
* Add ability to write modified drawio files ([#813](https://github.com/IBM/compliance-trestle/issues/813)) ([`ea814bf`](https://github.com/IBM/compliance-trestle/commit/ea814bfdcfb8e75e2812e182ec09b009e693312a))
* Build-component-definition ([#788](https://github.com/IBM/compliance-trestle/issues/788)) ([`9f7b1fe`](https://github.com/IBM/compliance-trestle/commit/9f7b1fec0efc017698ceef4c6bf77c132626ec93))
* Ssp filter allows filter of ssp based on profile ([#805](https://github.com/IBM/compliance-trestle/issues/805)) ([`494ba1b`](https://github.com/IBM/compliance-trestle/commit/494ba1b9a749c44657365f45fc88a8c4aa94ed73))
* Add centralised markdown API ([#797](https://github.com/IBM/compliance-trestle/issues/797)) ([`8582516`](https://github.com/IBM/compliance-trestle/commit/8582516f59a8258b513312185b8efdd4cb7a001e))

### Fix
* Preliminary fix for parameters where 'set parameter' is called an a value does not exist. ([#823](https://github.com/IBM/compliance-trestle/issues/823)) ([`d20f2b9`](https://github.com/IBM/compliance-trestle/commit/d20f2b9e6ca10c4fa829bb723d68ea3d06902cd0))
* Merge yaml header content when writing control ([#825](https://github.com/IBM/compliance-trestle/issues/825)) ([`8d0b3b0`](https://github.com/IBM/compliance-trestle/commit/8d0b3b0f3a6c5e3a47a42b46b77081a700947d6b))
* All Alter/Add of prop by_id ([#821](https://github.com/IBM/compliance-trestle/issues/821)) ([`a9047a8`](https://github.com/IBM/compliance-trestle/commit/a9047a83e0b0c64c34448f776a7e13fff77e6b2a))
* Ssp generate with alter props issue ([#819](https://github.com/IBM/compliance-trestle/issues/819)) ([`a1e4219`](https://github.com/IBM/compliance-trestle/commit/a1e421944ce11432b2b2832b8f669b65428f1b38))
* Allow markdown substitutions ([#812](https://github.com/IBM/compliance-trestle/issues/812)) ([`8d52d3e`](https://github.com/IBM/compliance-trestle/commit/8d52d3eb4aaa0a73685983114ffa38c494b9fec4))
* Handle hard line breaks ([#804](https://github.com/IBM/compliance-trestle/issues/804)) ([`b1e39c1`](https://github.com/IBM/compliance-trestle/commit/b1e39c1173b235a87981a2856081cd54aeac86e3))

## v0.26.0 (2021-10-20)
### Feature
* Add exclusion flags to trestle author header validate to allow practical use without a task name. ([#793](https://github.com/IBM/compliance-trestle/issues/793)) ([`d77408f`](https://github.com/IBM/compliance-trestle/commit/d77408f39e914bff3dfc20ecf91e3a982a49bf4e))
* Allow author edits and update of profile ([#771](https://github.com/IBM/compliance-trestle/issues/771)) ([`650b6c9`](https://github.com/IBM/compliance-trestle/commit/650b6c95eadfc68c5f0646761f57ac4b2542bb6c))
* Improve profile resolver to cover "adds" scenarios in fedramp & NIST 800-53 ([#766](https://github.com/IBM/compliance-trestle/issues/766)) ([`75911f3`](https://github.com/IBM/compliance-trestle/commit/75911f3f88c6b4d9a4adaea03a77db7f9a83faf9))
* Author catalog to support reading and writing controls and catalogs ([#734](https://github.com/IBM/compliance-trestle/issues/734)) ([`0a2bcea`](https://github.com/IBM/compliance-trestle/commit/0a2bcea49841c774a667aeb9368e776402db23cf))

### Fix
* Ssp issues ([#795](https://github.com/IBM/compliance-trestle/issues/795)) ([`3532e4e`](https://github.com/IBM/compliance-trestle/commit/3532e4ef7c7db33e6875a27123a4b6a4fa2655cc))
* Further refinements to CI pipeline ([#796](https://github.com/IBM/compliance-trestle/issues/796)) ([`b46c63b`](https://github.com/IBM/compliance-trestle/commit/b46c63be8a192993126b49c289e99ea5c10dc3a1))
* Correct broken guards of sonarqube actions. ([`9e10c1e`](https://github.com/IBM/compliance-trestle/commit/9e10c1e3fedc96c5f6e0b02651b77ce20d1421c5))
* Add missing __init__.py, which can cause issues with pytest. ([#792](https://github.com/IBM/compliance-trestle/issues/792)) ([`bc6fbf3`](https://github.com/IBM/compliance-trestle/commit/bc6fbf34843f3101edd4236f5dab904fa6a3606f))
* Document submodule requirement for testing. ([#782](https://github.com/IBM/compliance-trestle/issues/782)) ([`3e711a3`](https://github.com/IBM/compliance-trestle/commit/3e711a3416e8155a0e082b65e89060ac3e9d3227))
* Resolve bugs in xlsx to component definition ([#772](https://github.com/IBM/compliance-trestle/issues/772)) ([`ebff124`](https://github.com/IBM/compliance-trestle/commit/ebff1247b5bc9abf615f10ae943b0fdff3644507))
* Remove two bugs generated from unraised exceptions. ([#777](https://github.com/IBM/compliance-trestle/issues/777)) ([`5f698a6`](https://github.com/IBM/compliance-trestle/commit/5f698a6c28c84a9eb9595ddd1248ce29f149895a))
* Remove use of http aligning with zero trust principles. ([#770](https://github.com/IBM/compliance-trestle/issues/770)) ([`5b0240c`](https://github.com/IBM/compliance-trestle/commit/5b0240cfa83f89d5182e04efa91feb4eb06ad8fd))
* **security:** Remove user name from logs ([#767](https://github.com/IBM/compliance-trestle/issues/767)) ([`4d075b8`](https://github.com/IBM/compliance-trestle/commit/4d075b89776552a1f58751674e2056ac7afac3cc))
* **cli:** Correctly capture return codes ([#760](https://github.com/IBM/compliance-trestle/issues/760)) ([`170d911`](https://github.com/IBM/compliance-trestle/commit/170d9117dc318e39fa43249e424dcf244614ff1a))
* Added more checks for pylint. ([#758](https://github.com/IBM/compliance-trestle/issues/758)) ([`2443ced`](https://github.com/IBM/compliance-trestle/commit/2443cedf0ad7f7357aa4a1606fe7ddc8f6f3830b))
* Adding automated tests of binary distribution validate release. ([#756](https://github.com/IBM/compliance-trestle/issues/756)) ([`c0b6748`](https://github.com/IBM/compliance-trestle/commit/c0b67485cd6e5619bbe4654d651931ce378315ca))
* Ignore hidden files throughout the project ([#755](https://github.com/IBM/compliance-trestle/issues/755)) ([`aec1df4`](https://github.com/IBM/compliance-trestle/commit/aec1df4e80168998a368d951861e62b502ca7fae))

## v0.25.1 (2021-09-30)
### Fix
* Emergency fix for trestle packaging. ([#751](https://github.com/IBM/compliance-trestle/issues/751)) ([`8fedeaa`](https://github.com/IBM/compliance-trestle/commit/8fedeaa641e7817fb4092224a315e1a38166078e))

## v0.25.0 (2021-09-29)
### Feature
* Osco results remove scc_goal_description ([#736](https://github.com/IBM/compliance-trestle/issues/736)) ([`f687a3d`](https://github.com/IBM/compliance-trestle/commit/f687a3dcc44590a60f777d38eafe4013d54909e6))

### Fix
* Ensure a minimimal code base is delivered via pypi ([#741](https://github.com/IBM/compliance-trestle/issues/741)) ([`03557bd`](https://github.com/IBM/compliance-trestle/commit/03557bdd44980899342665bac2d1905489981a75))
* Adding extra documentation for element path. ([#735](https://github.com/IBM/compliance-trestle/issues/735)) ([`bc32371`](https://github.com/IBM/compliance-trestle/commit/bc32371e3f81adab5cd4621055421f2acb05c566))
* Test files to confirm and close issues ([#732](https://github.com/IBM/compliance-trestle/issues/732)) ([`e87eb84`](https://github.com/IBM/compliance-trestle/commit/e87eb84aabffd842275a673e63e42c75bd418203))

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