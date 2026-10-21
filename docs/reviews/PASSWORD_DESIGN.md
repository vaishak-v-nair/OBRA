# Password policy design review

Scope: existing app form and its validation states. No DESIGN.md is present; globals.css and the owner's Soft Minimal/Graphite Mint values are the authority. The designer binary was checked and is unavailable, so the fallback HTML sketch is at C:/Users/vaish/.gstack/projects/OBRA/designs/password-policy-20261019/policy.html. It is a design artifact, not live app evidence. Initial plan completeness8/10; this review specifies the missing error association and exact-input behavior.

## 1. Information architecture —9/10

The existing headline, brief description, visible field labels, password help, submit action and alternate sign-in link form the hierarchy. Preserve that sequence; creation guidance belongs next to the password input and must not appear as a new restriction on signin. Add aria-describedby to associate the help text with the field without changing layout.

```text
ORBA shell -> account heading -> labeled fields ->15..128 help -> alert -> submit
                                                  signin link -> current-password form
```

## 2. State coverage —9/10

| Feature | Loading | Empty | Error | Success | Partial |
|---|---|---|---|---|---|
| Signup | Existing disabled Please wait action after actual submit | Visible labels and policy help, required fields | Alert, unchanged password, submit available | Refresh authenticated identity then navigate | No success before refresh/identity confirmation |
| Signin | Same existing busy lock | Current-password autocomplete, no new15 minimum | Safe credential/server alert, unchanged entry | Actual authenticated workspace | Preserve existing network error behavior |
| Paste | No progress display | Normal editable input | Reject129 code points without clipping or POST | Full accepted value enters normal submit | Editing a rejected entry remains possible |

The policy check must precede the lock so invalid input never strands a busy button. Do not translate a server error into a green toast. The input stays a native password field without paste interception.

## 3. User journey —9/10

| Step | User action | User concern | Design answer |
|---|---|---|---|
| 1 | Open signup | What is required? | Concise15-128 helper attached to Password |
| 2 | Paste passphrase | Was it clipped? | Preserve full input, validate without mutation |
| 3 | Submit14/129 | Can I correct this? | Visible length error and still-editable field |
| 4 | Submit valid value | Did it work? | Existing busy state then real authenticated navigation |
| 5 | Return with old12 password | Am I locked out? | Signin retains current-password and1-128 acceptance |

The first five seconds orient through clear labels, the next minutes support correction and password managers, and returning users retain a stable signin experience. No forced reset message or new recovery action is invented. Failure copy describes a limit, not a security guarantee.

## 4. Intentionality / slop risk —9/10

This is app UI with one account action, not a marketing page. No cards, illustrations, gradients, decorative badges or progress simulation are added. Only the actual policy helper and validation behavior change; the screenshot/layout review should compare the existing shell rather than redesign it.

## 5. Design-system alignment —9/10

Reuse semantic tokens, standard-form, form-note, error-message and Button. Both themes inherit the current surface/text/accent choices without inline colors in product code. No new component, typography system or dependency is justified; the external sketch uses the exact palette as an illustrative reference only.

## 6. Responsive and accessibility —9/10

All three existing viewports remain in the browser matrix. Visible labels, keyboard focus, native form submission, password-manager autocomplete and the existing role=alert are preserved. Associate helper text by useId/aria-describedby; do not disable clipboard actions, add composition patterns or store values in browser storage. Unicode boundaries and long pasted input must be tested in both auth modes, not assumed from native attributes.

## 7. Unresolved choices —10/10

The user already chose15, so there is no remaining length/taste decision.128 is the existing safe upper bound and exceeds the requested64-character support; removing native clipping does not remove the server bound. Whitespace-only rejection remains server-authoritative, avoiding a new client Unicode-whitespace dialect. Browser errors keep values for correction and never print them.

## Litmus scorecard and completion

| Check | Primary judgment |
|---|---|
| Product recognizable | Yes, retained ORBA shell |
| One anchor | Yes, account heading/action |
| Scan understandable | Yes, fields/help/action |
| One job per section | Yes, signup or signin |
| Cards necessary | No new cards |
| Motion useful | No new motion needed |
| Premium without shadows | Yes, existing tokens/spacing |

What exists: AuthForm, native labels/input, Button, tokens and responsive shell. Not in scope: reset UI, show-password redesign, new navigation or visual identity. No new TODO is warranted; future recovery is already tracked. Independent in-host judgments will be appended before DX starts. These scores assess specified design coverage; they do not claim browser tests have run.

Independent in-host voice: PASSWORD_DESIGN_VOICE.md, same model family. Both reviews agree on the7 dimensions/litmus direction; no outside-model consensus is claimed. Field-associated errors, code-point validation before the lock and actual native clipboard/keyboard coverage are required refinements. Pre-existing network-copy and session-refresh findings are explicitly bounded and do not introduce a session-library rewrite. The HTML sketch was rendered via actual Chromium and viewed as a PNG; no new paid model or fake app evidence was involved. Final specified design coverage9/10, no unresolved decision.
