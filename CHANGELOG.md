# Compliance-trestle changelog


<!--next-version-placeholder-->

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