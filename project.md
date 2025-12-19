
### Copilot Instructions – File Naming Pattern Selection Step (CLI)

**Goal**
Add a new CLI step *after* the user selects which CSV keys will be included. This step allows the user to define the file naming pattern using those keys, based on **selection order**.

---

### Required Behavior

#### 1. Step Placement

* Execute this step **after** the “Select keys to include” step.
* Only use keys already selected in the previous step.

---

#### 2. Display Logic

* Show an interactive list with **only the previously selected keys**.
* All keys start **unselected**.
* Keys can be toggled **on and off**.
* The **order in which keys are selected matters** and must be preserved.

---

#### 3. Controls

* **Up / Down arrows** → navigate
* **Spacebar** → select or deselect a key
* **Enter** → confirm selection and move to the next step

---

#### 4. Selection & Ordering Rules

* When a key is selected (Space):

  * Assign it the next available order index (1, 2, 3, …).
* When a key is deselected (Space again):

  * Remove it from the ordered list.
  * Recalculate the ordering so remaining selections stay sequential.
* A key can only appear once in the order list.

---

#### 5. Visual Feedback

* Each selected key must show its **selection order** (e.g. `[1]`, `[2]`).
* Unselected keys show no index.
* The UI must make it clear that **order defines filename structure**.

---

#### 6. Naming Pattern Construction

* Build the base filename by concatenating the **values** of the selected keys (not the key names).
* Use the selection order to determine position.
* Join each value using:

  ```
  <Value 1> - <Value 2> - <Value 3>
  ```

---

#### 7. Filename Uniqueness

* Before writing a file, check if a file with the same base name already exists.
* If it exists, append a **non-repeating sequential integer**:

  ```
  <Base Name>
  <Base Name> - 2
  <Base Name> - 3
  ```
* Only append the number when necessary.

---

#### 8. Example (Conceptual – Do Not Hardcode)

Selected keys in order:

1. finding type
2. source
3. issue date

Generated filename:

```
{{Finding Type Value}} - {{Source Value}} - {{Issue Date Value}} - {{Sequential Integer If Needed}}
```

---

#### 9. Constraints

* Do **not** hardcode key names.
* Use existing selected-key data from the previous step.
* This step must work with **any CSV schema**.
* Keep this logic isolated so it can be reused or skipped later.

---

#### 10. UX Requirements

* Clearly label the step, e.g.:

  ```
  Step X: Select file naming pattern (Space to toggle, order matters)
  ```
* Show a **live filename preview** as selections change.
* Allow Enter to proceed only after at least one key is selected.

---

### Output of This Step

* An **ordered array of selected keys** for naming.
* A reusable filename generator that:

  * Receives a row’s values
  * Returns a safe, unique filename string
