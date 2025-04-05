[![GitHub Super-Linter](https://github.com/Azure/review-checklists/workflows/Lint%20Code%20Base/badge.svg)](https://github.com/marketplace/actions/super-linter)

# Azure Review Checklists

A common request of many organisations, starting with the public cloud, is to have their design double-checked to make sure that best practices are being followed. The scope of this exercise could vary, from generic Azure landing zones to workload-specific deployments.

When doing Azure design reviews (or any review for that matter), Microsoft employees and Microsoft partners often leverage Excel spreadsheets as the medium of choice to document findings and track design improvements and recommendations. A problem with Excel spreadsheets is that they are not easily subject to revision control. Additionally, team collaboration with branching, issues, pull requests, reviews, and others is difficult at best—impossible in most cases.

![](./pictures/overview.png)

There are three ways to use these checklists.

1) Via [Excel](./spreadsheet/README.md)
2) Via Web Application hosted at [https://aka.ms/ftaaas](https://aka.ms/ftaaas).
3) [Azure Resource Graph Queries](./scripts/README.md)

## Reporting errors and contributing

Please feel free to [open an issue](https://github.com/Azure/review-checklists/issues/new/choose) or create a PR if you find any error or missing information in the checklists, following the [Contributing guidelines](./CONTRIBUTING.md).

## Checklists

Summary of checklists supported and the respective responsible owners:

| Checklist | Status | CodeOwners |
| --- | --- | --- |
| Azure Landing Zone  | GA | FTA-ALZ-vTeam, ALZ-checklist-contributors  |
| AI Landing Zone  | Preview | [@mbilalamjad](https://github.com/mbilalamjad) [@prwani](https://github.com/prwani)  |
| WAF | GA | Dynamically generated |
| AKS | GA | [@msftnadavbh](https://github.com/msftnadavbh) [@seenu433](https://github.com/seenu433) [@erjosito](https://github.com/erjosito) |
| ARO | Preview | [@msftnadavbh](https://github.com/msftnadavbh) [@naioja](https://github.com/naioja) [@erjosito](https://github.com/erjosito) |
| AVD | GA | [@igorpag](https://github.com/igorpag) [@mikewarr](https://github.com/mikewarr) [@bagwyth](https://github.com/bagwyth) |
| Cost | GA | [@brmoreir](https://github.com/brmoreir) [@pea-ms](https://github.com/pea-ms) |
| Multitenancy | GA | [@arsenvlad](https://github.com/arsenvlad) [@cherchyk](https://github.com/cherchyk) |
| Application Delivery Networking | GA | [@erjosito](https://github.com/erjosito) [@andredewes](https://github.com/andredewes) |
| AVS design | Preview | [@fskelly](https://github.com/fskelly) [@mgodfrey50](https://github.com/mgodfrey50) [@robinher](https://github.com/robinher) |
| AVS implementation | Preview | [@fskelly](https://github.com/fskelly) [@mgodfrey50](https://github.com/mgodfrey50) [@robinher](https://github.com/robinher) |
| SAP | GA | [@NaokiIgarashi](https://github.com/NaokiIgarashi) [@AlastairMorrison](https://github.com/AlastairMorrison) [@mottach](https://github.com/mottach) |
| API Management | Preview | [@andredewes](https://github.com/andredewes) [@seenu433](https://github.com/seenu433) |
| Stack HCI | Preview | [@mbrat2005](https://github.com/mbrat2005) [@steveswalwell](https://github.com/steveswalwell) [@igomaa](https://github.com/igomaa) |
| Spring Apps | Preview | [@bappadityams](https://github.com/) [@vermegi](https://github.com/vermegi) [@fmustaf](https://github.com/fmustaf) |
| Azure DevOps | Preview | [@roshair](https://github.com/roshair) |
| SQL Migration | Preview | [@karthikyella](https://github.com/karthikyella) [@dbabulldog-repo](https://github.com/dbabulldog-repo) |
| Security | Deprecated | [@mgodfrey50](https://github.com/mgodfrey50) [@rudneir2](https://github.com/rudneir2) |

## Disclaimer

- This is not official Microsoft documentation or software.
- This is not an endorsement or a sign-off of an architecture or a design.
- This code sample is provided "AS IT IS" without warranty of any kind, either expressed or implied, including but not limited to the implied warranties of merchantability and/or fitness for a particular purpose.
- This sample is not supported under any Microsoft standard support program or service.
- Microsoft further disclaims all implied warranties, including, without limitation, any implied warranties of merchantability or fitness for a particular purpose.
- The entire risk arising out of the use or performance of the sample and documentation remains with you.
- In no event shall Microsoft, its authors, or anyone else involved in the creation, production, or delivery of the script be liable for any damages whatsoever (including, without limitation, damages for loss of business profits, business interruption, loss of business information, or other pecuniary loss) arising out of the use of or inability to use the sample or documentation, even if Microsoft has been advised of the possibility of such damages
