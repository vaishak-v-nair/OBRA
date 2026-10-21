# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: pm-live.spec.ts >> real model plan, editable criteria, persisted approval and unrelated-user denial
- Location: tests-live\pm-live.spec.ts:7:5

# Error details

```
Test timeout of 300000ms exceeded.
```

```
Error: locator.selectOption: Test timeout of 300000ms exceeded.
Call log:
  - waiting for locator('#product-plan').getByLabel('Disposition (conf_platform_choice)', { exact: true })

```

# Page snapshot

```yaml
- generic [ref=f1e1]:
  - generic [ref=f1e2]:
    - link "Skip to content" [ref=f1e3] [cursor=pointer]:
      - /url: "#main"
    - complementary "Workspace navigation" [ref=f1e4]:
      - link "orba ." [ref=f1e6] [cursor=pointer]:
        - /url: /
        - generic [aria-hidden] [ref=f1e7]: o
        - text: orba
        - generic [ref=f1e8]: .
      - generic [ref=f1e9]:
        - generic [ref=f1e10]: L
        - generic [ref=f1e11]:
          - generic [ref=f1e12]: Workspace
          - combobox "Workspace" [ref=f1e13]:
            - option "Select workspace" [disabled]
            - option "Live product planning" [selected]
      - link "New project" [ref=f1e14] [cursor=pointer]:
        - /url: /projects/new
      - paragraph [ref=f1e16]: WORKSPACE
      - navigation "Main navigation" [ref=f1e17]:
        - link "Chat" [ref=f1e18] [cursor=pointer]:
          - /url: /
        - link "Projects" [ref=f1e22] [cursor=pointer]:
          - /url: /projects
        - link "Skills" [ref=f1e28] [cursor=pointer]:
          - /url: /skills
        - link "Contribute" [ref=f1e33] [cursor=pointer]:
          - /url: /contribute
        - link "Workspaces" [ref=f1e39] [cursor=pointer]:
          - /url: /workspaces
        - link "Activity" [ref=f1e44] [cursor=pointer]:
          - /url: /activity
      - generic [ref=f1e48]:
        - link "Settings" [ref=f1e49] [cursor=pointer]:
          - /url: /settings
        - generic [ref=f1e53]:
          - generic [ref=f1e54]: O
          - group [ref=f1e55]:
            - generic "Account · ORBA Tester" [ref=f1e56] [cursor=pointer]
    - generic [ref=f1e57]:
      - banner [ref=f1e58]:
        - generic [ref=f1e59]:
          - generic [ref=f1e60]: Workspace
          - strong [ref=f1e63]: Projects
        - generic [ref=f1e64]:
          - generic [ref=f1e65]: Product planning
          - button "Toggle color theme" [ref=f1e66] [cursor=pointer]
      - main [ref=f1e73]:
        - generic [ref=f1e75]:
          - link "All projects" [ref=f1e76] [cursor=pointer]:
            - /url: /projects
          - generic [ref=f1e79]:
            - generic [ref=f1e83]:
              - paragraph [ref=f1e84]: PROJECT OVERVIEW
              - heading "Build a simple personal habit tracker with daily check-ins, a streak counter, and a weekly summary. The first version is" [level=1] [ref=f1e85]
            - generic [ref=f1e86]: Created
          - generic [ref=f1e90]:
            - text: Created
            - time [ref=f1e91]: 10/19/2026, 12:03:53 PM
          - generic [ref=f1e92]:
            - heading "Where it begins" [level=2] [ref=f1e93]
            - paragraph [ref=f1e94]: Your original project description
            - paragraph [ref=f1e95]: Build a simple personal habit tracker with daily check-ins, a streak counter, and a weekly summary. The first version is for one user and does not require social features.
            - button "Edit project" [ref=f1e96] [cursor=pointer]
          - region [ref=f1e97]:
            - generic [ref=f1e98]:
              - generic [ref=f1e99]:
                - paragraph [ref=f1e100]: PRODUCT MANAGER
                - heading "Product Plan" [level=2] [ref=f1e101]
              - generic [ref=f1e105]: One planning agent
            - paragraph [ref=f1e106]: Turn your idea into reviewable requirements. Generation uses your configured AI provider and may incur usage.
            - group [ref=f1e107]:
              - generic "Generate another product plan" [ref=f1e108] [cursor=pointer]
            - status [ref=f1e109]: The model response was validated and saved as a draft. Review it before approval.
            - button "Check status" [ref=f1e113] [cursor=pointer]
            - generic [ref=f1e114]:
              - generic [ref=f1e115]:
                - generic [ref=f1e116]:
                  - text: Plan version
                  - combobox "Plan version" [ref=f1e117]:
                    - option "Version 1 · draft · revision 1" [selected]
                - generic [ref=f1e118]: draft
              - paragraph [ref=f1e119]: Version 1 · revision 1 · AI generated draft
              - group [ref=f1e120]:
                - generic "Generation evidence · gemini-3.8-flash" [ref=f1e121] [cursor=pointer]
              - group [ref=f1e122]:
                - generic "Exact generation input snapshot" [ref=f1e123] [cursor=pointer]
              - form "Edit product plan" [ref=f1e124]:
                - group "Draft requirements" [ref=f1e125]:
                  - paragraph [ref=f1e127]: Changes stay in this page until saved. The server records your identity on changed requirements; existing source evidence is preserved.
                  - generic [ref=f1e128]:
                    - generic [ref=f1e129]: Product name
                    - textbox "Product name" [ref=f1e130]: Personal Habit Tracker
                  - generic [ref=f1e131]:
                    - generic [ref=f1e132]: Summary
                    - textbox "Summary" [ref=f1e133]: A single-user habit tracking application providing daily check-ins, streak calculation, and weekly performance summaries.
                  - generic [ref=f1e134]:
                    - generic [ref=f1e135]: Problem statement
                    - textbox "Problem statement" [ref=f1e136]: Individuals need a simple mechanism to record habit completion daily and review progress without social clutter.
                  - generic [ref=f1e137]:
                    - generic [ref=f1e138]: Proposed solution
                    - textbox "Proposed solution" [ref=f1e139]: Deliver a streamlined single-user application featuring habit creation, one-click daily check-ins, automated streak tracking, and weekly progress overviews.
                  - group [ref=f1e140]:
                    - generic "Target users (1)" [ref=f1e141] [cursor=pointer]
                  - group [ref=f1e142]:
                    - generic "User goals (3)" [ref=f1e143] [cursor=pointer]
                  - group [ref=f1e144]:
                    - generic "In scope (3)" [ref=f1e145] [cursor=pointer]
                  - group [ref=f1e146]:
                    - generic "Out of scope (1)" [ref=f1e147] [cursor=pointer]
                  - group [ref=f1e148]:
                    - generic "Functional requirements (3)" [ref=f1e149] [cursor=pointer]
                    - generic [ref=f1e150]:
                      - generic [ref=f1e151]:
                        - generic [ref=f1e152]:
                          - generic [ref=f1e153]: Functional requirements 1
                          - textbox "Functional requirements 1" [ref=f1e154]: The system shall allow marking a habit as completed for the current day.
                        - button "Remove Functional requirements 1" [ref=f1e155] [cursor=pointer]: Remove
                        - generic [ref=f1e156]: req_checkin
                      - generic [ref=f1e157]:
                        - generic [ref=f1e158]:
                          - generic [ref=f1e159]: Functional requirements 2
                          - textbox "Functional requirements 2" [ref=f1e160]: The system shall calculate and display the current consecutive day streak for each habit.
                        - button "Remove Functional requirements 2" [ref=f1e161] [cursor=pointer]: Remove
                        - generic [ref=f1e162]: req_streak
                      - generic [ref=f1e163]:
                        - generic [ref=f1e164]:
                          - generic [ref=f1e165]: Functional requirements 3
                          - textbox "Functional requirements 3" [ref=f1e166]: The system shall display a weekly summary showing completion history across the past 7 days.
                        - button "Remove Functional requirements 3" [ref=f1e167] [cursor=pointer]: Remove
                        - generic [ref=f1e168]: req_summary
                      - button "Add functional requirements item" [ref=f1e169] [cursor=pointer]
                  - group [ref=f1e170]:
                    - generic "Nonfunctional requirements (1)" [ref=f1e171] [cursor=pointer]
                  - group [ref=f1e172]:
                    - generic "Prerequisites (0)" [ref=f1e173] [cursor=pointer]
                  - group [ref=f1e174]:
                    - generic "Assumptions (1)" [ref=f1e175] [cursor=pointer]
                  - group [ref=f1e176]:
                    - generic "Risks (1)" [ref=f1e177] [cursor=pointer]
                  - group [ref=f1e178]:
                    - generic "Open questions (1)" [ref=f1e179] [cursor=pointer]
                  - heading "Epics and stories" [level=3] [ref=f1e180]
                  - region "Edit epic 1" [ref=f1e181]:
                    - generic [ref=f1e182]:
                      - generic [ref=f1e183]: Epic 1 title
                      - textbox "Epic 1 title" [ref=f1e184]: Core Habit Tracking
                    - generic [ref=f1e185]:
                      - generic [ref=f1e186]: Epic 1 goal
                      - textbox "Epic 1 goal" [ref=f1e187]: Provide single-user habit recording, streak tracking, and weekly progress reporting.
                    - generic [ref=f1e188]:
                      - text: Epic 1 priority
                      - combobox "Epic 1 priority" [ref=f1e189]:
                        - option "P0" [selected]
                        - option "P1"
                        - option "P2"
                        - option "P3"
                    - button "Remove epic 1" [disabled]
                    - region "Edit story story_checkin" [ref=f1e190]:
                      - generic [ref=f1e191]:
                        - generic [ref=f1e192]: Story title (story_checkin)
                        - textbox "Story title (story_checkin)" [ref=f1e193]: Daily Habit Check-in
                      - generic [ref=f1e194]:
                        - generic [ref=f1e195]: User story (story_checkin)
                        - textbox "User story (story_checkin)" [ref=f1e196]: As a habit tracker, I want to record my daily habit completion, so that I maintain accountability.
                      - paragraph [ref=f1e197]: As a [user], I want [capability], so that [benefit].
                      - generic [ref=f1e198]:
                        - generic [ref=f1e199]: Story description (story_checkin)
                        - textbox "Story description (story_checkin)" [ref=f1e200]: Allows the user to mark a habit as done for the current date.
                      - generic [ref=f1e201]:
                        - text: Story priority (story_checkin)
                        - combobox "Story priority (story_checkin)" [ref=f1e202]:
                          - option "P0" [selected]
                          - option "P1"
                          - option "P2"
                          - option "P3"
                      - generic [ref=f1e203]:
                        - text: Requirement references (story_checkin)
                        - listbox "Requirement references (story_checkin)" [ref=f1e204]:
                          - 'option "req_checkin: The system shall allow marking a habit as completed for the current day." [selected] [ref=f1e205]'
                          - 'option "req_streak: The system shall calculate and display the current consecutive day streak for each habit." [ref=f1e206]'
                          - 'option "req_summary: The system shall display a weekly summary showing completion history across the past 7 days." [ref=f1e207]'
                          - 'option "nfr_local_storage: The application shall persist data locally on the client device." [ref=f1e208]'
                      - generic [ref=f1e209]:
                        - text: Dependencies (story_checkin)
                        - listbox "Dependencies (story_checkin)" [ref=f1e210]:
                          - 'option "story_streaks: Streak Counter Calculation" [ref=f1e211]'
                          - 'option "story_summary: Weekly Progress Summary" [ref=f1e212]'
                      - paragraph [ref=f1e213]: Use Ctrl or Command to select multiple items or clear a dependency. Removing a referenced requirement or story requires correcting its references before saving.
                      - generic [ref=f1e214]:
                        - generic [ref=f1e215]:
                          - generic [ref=f1e216]: Given (ac_checkin_success)
                          - textbox "Given (ac_checkin_success)" [ref=f1e217]: An active habit is listed for today and is currently unmarked
                        - generic [ref=f1e218]:
                          - generic [ref=f1e219]: When (ac_checkin_success)
                          - textbox "When (ac_checkin_success)" [ref=f1e220]: The user submits a completion check-in for today
                        - generic [ref=f1e221]:
                          - generic [ref=f1e222]: Then (ac_checkin_success)
                          - textbox "Then (ac_checkin_success)" [active] [ref=f1e223]: The saved daily check-in is still visible after the page is reloaded.
                        - button "Remove criterion 1" [ref=f1e224] [cursor=pointer]
                      - generic [ref=f1e225]:
                        - generic [ref=f1e226]:
                          - generic [ref=f1e227]: Given (ac_checkin_toggle)
                          - textbox "Given (ac_checkin_toggle)" [ref=f1e228]: A habit has been marked completed today
                        - generic [ref=f1e229]:
                          - generic [ref=f1e230]: When (ac_checkin_toggle)
                          - textbox "When (ac_checkin_toggle)" [ref=f1e231]: The user removes the completion mark
                        - generic [ref=f1e232]:
                          - generic [ref=f1e233]: Then (ac_checkin_toggle)
                          - textbox "Then (ac_checkin_toggle)" [ref=f1e234]: The habit returns to incomplete for today
                        - button "Remove criterion 2" [ref=f1e235] [cursor=pointer]
                      - generic [ref=f1e236]:
                        - button "Add acceptance criterion" [ref=f1e237] [cursor=pointer]
                        - button "Remove story" [ref=f1e238] [cursor=pointer]
                    - region "Edit story story_streaks" [ref=f1e239]:
                      - generic [ref=f1e240]:
                        - generic [ref=f1e241]: Story title (story_streaks)
                        - textbox "Story title (story_streaks)" [ref=f1e242]: Streak Counter Calculation
                      - generic [ref=f1e243]:
                        - generic [ref=f1e244]: User story (story_streaks)
                        - textbox "User story (story_streaks)" [ref=f1e245]: As a habit tracker, I want to see my consecutive completion streak, so that I stay motivated.
                      - paragraph [ref=f1e246]: As a [user], I want [capability], so that [benefit].
                      - generic [ref=f1e247]:
                        - generic [ref=f1e248]: Story description (story_streaks)
                        - textbox "Story description (story_streaks)" [ref=f1e249]: Calculates and presents consecutive daily completions for each habit.
                      - generic [ref=f1e250]:
                        - text: Story priority (story_streaks)
                        - combobox "Story priority (story_streaks)" [ref=f1e251]:
                          - option "P0" [selected]
                          - option "P1"
                          - option "P2"
                          - option "P3"
                      - generic [ref=f1e252]:
                        - text: Requirement references (story_streaks)
                        - listbox "Requirement references (story_streaks)" [ref=f1e253]:
                          - 'option "req_checkin: The system shall allow marking a habit as completed for the current day." [ref=f1e254]'
                          - 'option "req_streak: The system shall calculate and display the current consecutive day streak for each habit." [selected] [ref=f1e255]'
                          - 'option "req_summary: The system shall display a weekly summary showing completion history across the past 7 days." [ref=f1e256]'
                          - 'option "nfr_local_storage: The application shall persist data locally on the client device." [ref=f1e257]'
                      - generic [ref=f1e258]:
                        - text: Dependencies (story_streaks)
                        - listbox "Dependencies (story_streaks)" [ref=f1e259]:
                          - 'option "story_checkin: Daily Habit Check-in" [selected] [ref=f1e260]'
                          - 'option "story_summary: Weekly Progress Summary" [ref=f1e261]'
                      - paragraph [ref=f1e262]: Use Ctrl or Command to select multiple items or clear a dependency. Removing a referenced requirement or story requires correcting its references before saving.
                      - generic [ref=f1e263]:
                        - generic [ref=f1e264]:
                          - generic [ref=f1e265]: Given (ac_streak_increment)
                          - textbox "Given (ac_streak_increment)" [ref=f1e266]: A habit had a streak of N days yesterday and is marked complete today
                        - generic [ref=f1e267]:
                          - generic [ref=f1e268]: When (ac_streak_increment)
                          - textbox "When (ac_streak_increment)" [ref=f1e269]: The streak recalculates
                        - generic [ref=f1e270]:
                          - generic [ref=f1e271]: Then (ac_streak_increment)
                          - textbox "Then (ac_streak_increment)" [ref=f1e272]: The streak value is displayed as N + 1 days
                        - button "Remove criterion 1" [ref=f1e273] [cursor=pointer]
                      - generic [ref=f1e274]:
                        - generic [ref=f1e275]:
                          - generic [ref=f1e276]: Given (ac_streak_reset)
                          - textbox "Given (ac_streak_reset)" [ref=f1e277]: A habit was not marked complete yesterday or today
                        - generic [ref=f1e278]:
                          - generic [ref=f1e279]: When (ac_streak_reset)
                          - textbox "When (ac_streak_reset)" [ref=f1e280]: The user views the habit streak
                        - generic [ref=f1e281]:
                          - generic [ref=f1e282]: Then (ac_streak_reset)
                          - textbox "Then (ac_streak_reset)" [ref=f1e283]: The streak counter displays 0 days
                        - button "Remove criterion 2" [ref=f1e284] [cursor=pointer]
                      - generic [ref=f1e285]:
                        - button "Add acceptance criterion" [ref=f1e286] [cursor=pointer]
                        - button "Remove story" [ref=f1e287] [cursor=pointer]
                    - region "Edit story story_summary" [ref=f1e288]:
                      - generic [ref=f1e289]:
                        - generic [ref=f1e290]: Story title (story_summary)
                        - textbox "Story title (story_summary)" [ref=f1e291]: Weekly Progress Summary
                      - generic [ref=f1e292]:
                        - generic [ref=f1e293]: User story (story_summary)
                        - textbox "User story (story_summary)" [ref=f1e294]: As a habit tracker, I want to review a weekly summary, so that I understand my recent performance.
                      - paragraph [ref=f1e295]: As a [user], I want [capability], so that [benefit].
                      - generic [ref=f1e296]:
                        - generic [ref=f1e297]: Story description (story_summary)
                        - textbox "Story description (story_summary)" [ref=f1e298]: Displays completion records across a 7-day rolling or calendar window.
                      - generic [ref=f1e299]:
                        - text: Story priority (story_summary)
                        - combobox "Story priority (story_summary)" [ref=f1e300]:
                          - option "P0"
                          - option "P1" [selected]
                          - option "P2"
                          - option "P3"
                      - generic [ref=f1e301]:
                        - text: Requirement references (story_summary)
                        - listbox "Requirement references (story_summary)" [ref=f1e302]:
                          - 'option "req_checkin: The system shall allow marking a habit as completed for the current day." [ref=f1e303]'
                          - 'option "req_streak: The system shall calculate and display the current consecutive day streak for each habit." [ref=f1e304]'
                          - 'option "req_summary: The system shall display a weekly summary showing completion history across the past 7 days." [selected] [ref=f1e305]'
                          - 'option "nfr_local_storage: The application shall persist data locally on the client device." [ref=f1e306]'
                      - generic [ref=f1e307]:
                        - text: Dependencies (story_summary)
                        - listbox "Dependencies (story_summary)" [ref=f1e308]:
                          - 'option "story_checkin: Daily Habit Check-in" [selected] [ref=f1e309]'
                          - 'option "story_streaks: Streak Counter Calculation" [ref=f1e310]'
                      - paragraph [ref=f1e311]: Use Ctrl or Command to select multiple items or clear a dependency. Removing a referenced requirement or story requires correcting its references before saving.
                      - generic [ref=f1e312]:
                        - generic [ref=f1e313]:
                          - generic [ref=f1e314]: Given (ac_summary_view)
                          - textbox "Given (ac_summary_view)" [ref=f1e315]: Completed and missed check-ins exist over the past 7 days
                        - generic [ref=f1e316]:
                          - generic [ref=f1e317]: When (ac_summary_view)
                          - textbox "When (ac_summary_view)" [ref=f1e318]: The user opens the weekly summary view
                        - generic [ref=f1e319]:
                          - generic [ref=f1e320]: Then (ac_summary_view)
                          - textbox "Then (ac_summary_view)" [ref=f1e321]: A 7-day breakdown of completed vs missed days is displayed
                        - button "Remove criterion 1" [disabled]
                      - generic [ref=f1e322]:
                        - button "Add acceptance criterion" [ref=f1e323] [cursor=pointer]
                        - button "Remove story" [ref=f1e324] [cursor=pointer]
                    - button "Add user story" [ref=f1e325] [cursor=pointer]
                  - button "Add epic" [ref=f1e326] [cursor=pointer]
                  - heading "Items requiring confirmation" [level=3] [ref=f1e327]
                  - generic [ref=f1e328]:
                    - paragraph [ref=f1e329]:
                      - strong [ref=f1e330]: conf_platform_choice
                      - text: · Blocking
                    - paragraph [ref=f1e331]: Confirm target deployment platform (Web browser local storage vs. mobile application).
                    - generic [ref=f1e332]:
                      - text: Disposition (conf_platform_choice)
                      - combobox "Disposition (conf_platform_choice)" [ref=f1e333]:
                        - option "unresolved" [selected]
                        - option "resolved"
                        - option "deferred"
                    - paragraph [ref=f1e334]: A blocking item retains its original wording and evidence. Resolve it or defer it with a reason before approval.
                  - button "Add confirmation" [ref=f1e335] [cursor=pointer]
                - generic [ref=f1e336]:
                  - button "Save draft" [ref=f1e337] [cursor=pointer]
                  - button "Cancel editing" [ref=f1e338] [cursor=pointer]
                  - button "Inspect latest saved revision" [ref=f1e339] [cursor=pointer]
                - status [ref=f1e340]: Unsaved changes. Approval is unavailable until they are saved.
            - group [ref=f1e341]:
              - generic "Planning run history (1)" [ref=f1e342] [cursor=pointer]
          - generic [ref=f1e348]:
            - heading "Room for what comes next" [level=2] [ref=f1e349]
            - paragraph [ref=f1e350]: Architecture, tasks, additional agents, and delivery evidence will live here.
            - generic [ref=f1e351]: Coming in a later stage
      - contentinfo [ref=f1e355]:
        - generic [ref=f1e356]: Built for the way you think.
        - generic [ref=f1e357]: Local development workspace
  - alert [ref=f1e358]
```

# Test source

```ts
  1  | /** Mandatory REAL model-backed browser flow. No fixture-generated responses or intercepts. */
  2  | import {test,expect} from "@playwright/test";
  3  | import {execFileSync} from "node:child_process";
  4  | import {writeFileSync} from "node:fs";
  5  | import {signup,createWorkspace,signout} from "../tests/helpers";
  6  | 
  7  | test("real model plan, editable criteria, persisted approval and unrelated-user denial",async({page,browser})=>{
  8  |   execFileSync("uv",["run","--directory","../api","python","-m","scripts.prepare_tests"],{stdio:"pipe"});
  9  |   const email=`live-browser-${Date.now()}@example.com`;
  10 |   await signup(page,email);await signout(page);
  11 |   await page.getByLabel("Email",{exact:true}).fill(email);await page.getByLabel("Password",{exact:true}).fill("A long browser password!");await page.getByRole("button",{name:"Sign in",exact:true}).click();
  12 |   await expect(page.getByRole("heading",{name:"A home for your ideas"})).toBeVisible();
  13 |   await createWorkspace(page,"Live product planning");
  14 |   const brief="Build a simple personal habit tracker with daily check-ins, a streak counter, and a weekly summary. The first version is for one user and does not require social features.";
  15 |   await page.getByLabel("Project description",{exact:true}).fill(brief);
  16 |   const creation=page.waitForResponse(r=>r.request().method()==="POST" && r.url().endsWith("/api/v1/projects"));
  17 |   await page.getByRole("button",{name:"Create project",exact:true}).click();const project=await (await creation).json();
  18 |   const panel=page.locator("#product-plan");
  19 |   await panel.getByLabel("Additional instructions (optional)").fill("Keep this small: 1 epic, at most 3 stories and 6 criteria in total. Use concise text. Identify missing decisions explicitly.");
  20 |   const generation=page.waitForResponse(r=>r.request().method()==="POST" && r.url().endsWith("/pm-runs"),{timeout:260000});
  21 |   await panel.getByRole("button",{name:"Generate Product Plan",exact:true}).click();const response=await generation;
  22 |   expect(response.status(),await response.text()).toBe(201);const run=await response.json();
  23 |   await expect(panel.getByTestId("plan-state")).toHaveText("draft");
  24 |   const apiPlan=await (await page.request.get(`/api/v1/projects/${project.id}/pm-plans/${run.plan_id}`)).json();
  25 |   expect(apiPlan.generation.id).toBe(run.id);expect(apiPlan.document.epics.length).toBeGreaterThan(0);expect(apiPlan.document.epics[0].stories.length).toBeGreaterThan(0);expect(apiPlan.approved_by).toBeNull();
  26 |   await panel.getByRole("button",{name:"Edit draft",exact:true}).click();
  27 |   const criterion="The saved daily check-in is still visible after the page is reloaded.";
  28 |   await panel.getByLabel(/^Then \(/).first().fill(criterion);
> 29 |   for(const item of apiPlan.document.confirmations){if(item.blocking){await panel.getByLabel(`Disposition (${item.key})`,{exact:true}).selectOption("deferred");await panel.getByLabel(`Disposition reason (${item.key})`,{exact:true}).fill("The test owner explicitly defers this decision for this isolated planning verification.");}}
     |                                                                                                                                        ^ Error: locator.selectOption: Test timeout of 300000ms exceeded.
  30 |   const saveResponse=page.waitForResponse(r=>r.request().method()==="PUT" && r.url().endsWith(`/pm-plans/${run.plan_id}`));
  31 |   await panel.getByRole("button",{name:"Save draft",exact:true}).click();
  32 |   expect((await saveResponse).status()).toBe(200);
  33 |   await expect(panel.getByRole("form",{name:"Edit product plan",exact:true})).toHaveCount(0);
  34 |   await expect(panel.getByRole("status")).toContainText("saved");
  35 |   await expect(panel.getByText(criterion,{exact:false}).first()).toBeVisible();await page.reload();await expect(panel.getByText(criterion,{exact:false}).first()).toBeVisible();
  36 |   await panel.getByRole("button",{name:"Approve plan",exact:true}).click();await panel.getByRole("button",{name:"Confirm approval",exact:true}).click();await expect(panel.getByTestId("plan-state")).toHaveText("approved");
  37 |   await page.reload();await expect(panel.getByTestId("plan-state")).toHaveText("approved");
  38 |   const approved=await (await page.request.get(`/api/v1/projects/${project.id}/pm-plans/${run.plan_id}`)).json();expect(approved.approved_at).toBeTruthy();expect(approved.document.epics[0].stories[0].acceptance_criteria[0].then).toBe(criterion);
  39 |   const context=await browser.newContext();const outsider=await context.newPage();await signup(outsider,`live-outsider-${Date.now()}@example.com`);await createWorkspace(outsider,"Unrelated user");
  40 |   const denied=await outsider.request.get(`/api/v1/projects/${project.id}/pm-plans/${run.plan_id}`);expect(denied.status()).toBe(404);expect(await denied.text()).not.toContain(criterion);
  41 |   await outsider.goto(`/projects/${project.id}`);await expect(outsider.getByRole("main").getByRole("alert")).toHaveText("Project not found.");await expect(outsider.getByText(criterion,{exact:false})).toHaveCount(0);await context.close();
  42 |   writeFileSync("../../docs/evidence/stage03-live-browser.json",JSON.stringify({scenario:"Real browser Generate -> edit -> reload -> approve -> reload -> unrelated denial",http_status:response.status(),run_id:run.id,plan_id:run.plan_id,provider:run.provider,model:run.returned_model,provider_response_id:run.provider_response_id,provider_request_id:run.provider_request_id,usage:run.usage,state:approved.state,version:approved.version,revision:approved.revision,approved_by:approved.approved_by,approved_at:approved.approved_at,unrelated_http_status:denied.status(),mocks:false},null,2)+"\n");
  43 | });
  44 | 
```