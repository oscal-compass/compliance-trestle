# Compliance-trestle changelog


<!--next-version-placeholder-->

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