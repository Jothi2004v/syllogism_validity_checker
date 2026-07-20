# Syllogism Validity Checker

A web-based **Syllogism Validity Checker** built using **Python** and **Streamlit**. This application allows users to enter syllogistic premises and conclusions, then determines whether each conclusion logically follows from the given premises using Venn diagram reasoning and transitive inference rules.

---

## Features

- Add multiple premises
- Add one or more conclusions
- Supports the following statement types:
  - All A are B
  - Some A are B
  - Some A are not B
  - No A are B
- Supports:
  - Definite conclusions
  - Possibility conclusions
- Detects contradictory premises
- Performs transitive logical inference
- Detects complementary conclusion pairs
- Modern Streamlit user interface
- Add/Delete premises and conclusions
- Clear all premises or conclusions
- Displays whether each conclusion:
  - Follows
  - Does Not Follow
  - Either of two complementary conclusions follows

---

## Project Structure

```
Syllogism-Validity-Checker/
│
├── app.py              # Streamlit user interface
├── Logic.py            # Logical reasoning engine
├── requirements.txt
├── README.md
```

---

## Technologies Used

- Python 3.x
- Streamlit

---

## Installation

Clone the repository

```bash
git clone https://github.com/yourusername/Syllogism-Validity-Checker.git
```

Go to the project directory

```bash
cd Syllogism-Validity-Checker
```

Install the required packages

```bash
pip install -r requirements.txt
```

or

```bash
pip install streamlit
```

---

## Running the Application

Run

```bash
streamlit run app.py
```

The application will open automatically in your browser.

---

## How to Use

### Step 1

Add one or more premises.

Example:

```
All pens are scales
Some papers are pens
No scales are markers
```

---

### Step 2

Add one or more conclusions.

Example:

```
Some papers are scales
Some markers are papers
```

Choose the modifier if required:

- None
- Is a Definite
- Is a Possibility

---

### Step 3

Click **Check Validity**.

The application will analyze the logical relationships and display whether each conclusion:

- ✅ Follows
- ❌ Does Not Follow
- 🟡 Either conclusion follows (Complementary Pair)

---

## Logical Rules Implemented

The reasoning engine supports:

### Universal Statements

```
All A are B
```

### Existential Statements

```
Some A are B
Some A are not B
```

### Negative Statements

```
No A are B
```

### Transitive Inference

Examples:

```
All A are B
All B are C

⇒ All A are C
```

```
Some A are B
All B are C

⇒ Some A are C
```

```
All A are B
No B are C

⇒ No A are C
```

```
Some A are B
No B are C

⇒ Some A are not C
```

---

## Contradiction Detection

The application automatically detects contradictory premises.

Example:

```
All pens are books
Some pens are not books
```

or

```
Some pens are books
No pens are books
```

---

## Complementary Pair Detection

The application identifies complementary conclusions such as:

```
Some A are B
No A are B
```

and determines whether:

- One definitely follows
- The other definitely does not follow
- Either one may follow

---

## Example

### Premises

```
Some papers are pens
All pens are scales
No scales are markers
```

### Conclusions

```
Some papers are scales
Some markers are papers
```

### Output

```
Conclusion 1 Follows

Conclusion 2 Does Not Follow
```

---

## Future Improvements

- Graphical Venn Diagram generation
- Export results as PDF
- Save and load syllogisms
- Explanation of reasoning steps
- Dark mode
- Support for additional logical forms

---

## Author

**Jothi Prakash**

---

## License

This project is intended for educational and learning purposes.
