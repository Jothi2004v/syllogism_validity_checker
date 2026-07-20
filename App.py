import streamlit as st
import Logic

st.set_page_config(page_title="Syllogism", page_icon=":man_health_worker:", layout="wide")

#Heading
st.markdown("""
<style>

/* Main title */
.centered-title{
    color:#6666ff !important ;
    text-align:center;
    font-size: 52px ;
    font-weight: 800;
    font-style: italic;
}

/* Section headings */
div[data-testid="stMarkdownContainer"] h3{
    font-size:34px ;
    font-weight:800 ;
}

/* Buttons */
.stButton>button{
    background:#3366ff;
    color:white;
    border-radius:10px;
    border:none;
    font-size:18px;
    font-weight:700;
    padding:10px 20px;
}

.stButton>button:hover{
    background:linear-gradient(90deg,#1d4ed8,#6d28d9);
    transform:scale(1.02);
}

/* Input boxes */
.stTextInput input {
    font-size:18px;
    border-radius:10px; 
    box-shadow:none ;
    outline:none ;
}
            
.stTextInput div[data-baseweb="base-input"]{
    border:2px solid #3366ff !important;
    border-radius:10px !important;
    min-height:38px !important;
    box-shadow:none !important;
}

/* Select boxes - matched to the same 38px height as text inputs above */
.stSelectbox div[data-baseweb="select"]{
    min-height:38px !important;
    font-size:18px;
    border-radius:10px;
    border:2px solid #3366ff;
}

.stSelectbox div[data-baseweb="select"] > div{
    min-height:38px !important;
    display:flex;
    align-items:center;
}
            
.stSelectbox div[data-baseweb="select"]:focus-within{
    border:2px solid #3366ff ;
    box-shadow:none;
}
            
/* Make all input labels bigger and bold */
/* Labels of text_input, selectbox, etc. */
label[data-testid="stWidgetLabel"] p{
    font-size:18px ;
    font-weight:700 ;
    # color:#1e293b ;
}
            
/* Divider */
hr{
        border:1px solid #bebebe !important;
    }
            
.premise-card,
.conclusion-card{
    font-size:18px ;
    font-weight:600 ;
    line-height:1.6;
}
            
</style>
""", unsafe_allow_html=True)

st.markdown("<style>div.block-container{margin-top:-60px;}</style>", unsafe_allow_html=True)
st.markdown(
    """
    <h1 class="centered-title">Syllogism Validity Checker</h1>
    """,
    unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)

# Session state initialization
if "premises" not in st.session_state:
    st.session_state.premises = []

if "conclusions" not in st.session_state:
    st.session_state.conclusions = []

#options
Quantifier = ['All', 'Some','No']
Copula = ["are", "are not",'is','being']
Modifier = ["none","is a possibility", "is a definite"]

with st.container():
    st.subheader("📘*Add Premise*")
    col1, col2, col3, col4= st.columns(4)
    with col1:
        p_quantifier = st.selectbox("Quantifier", Quantifier, key="p_quantifier")
    with col2:
        p_subject = st.text_input("Subject", key="p_subject")
    with col3:
        p_copula = st.selectbox("Relation", Copula, key="p_copula")
    with col4:
        p_predicate = st.text_input("Predicate", key="p_predicate")

#Add button
if st.button("Add Premise"):
    if not p_subject.strip() or not p_predicate.strip():
        st.error("Subject and Predicate are required.")
    else:
        st.session_state.premises.append({
            "quantifier": p_quantifier,
            "subject": p_subject.strip(),
            "copula": p_copula,
            "predicate": p_predicate.strip(),
        })
        st.success("Premise added successfully.")

st.divider()

#Conclusion
with st.container():
        st.subheader("📗*Set Conclusion*")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            c_quantifier = st.selectbox("Quantifier", Quantifier, key="c_quantifier")
        with col2:
            c_subject = st.text_input("Subject", key="c_subject")
        with col3:
            c_copula = st.selectbox("Relation", Copula, key="c_copula")
        with col4:
            c_predicate = st.text_input("Predicate", key="c_predicate")
        with col5:
            c_modifier = st.selectbox("Modifier", Modifier, key="c_modifier")


if st.button("Set Conclusion"):
    if not c_subject.strip() or not c_predicate.strip():
        st.error("Subject and Predicate are required.")
    else:
        st.session_state.conclusions.append({
            "quantifier": c_quantifier,
            "subject": c_subject.strip(),
            "copula": c_copula,
            "predicate": c_predicate.strip(),
            "modifier": c_modifier
        })
        st.success("Conclusion added successfully.")

st.divider()

# Display premises
with st.expander("📄 Premises", expanded=True):
    if len(st.session_state.premises) == 0:
        st.info("No premises added.")
    else:
        for i, p in enumerate(st.session_state.premises):
            col1, col2 = st.columns([6,1])
            with col1:
                st.markdown(f"""
                                    <div class="premise-card" style="
                                    background:#eff6ff;
                                    padding:15px;
                                    color:#1e3a8a;
                                    border-radius:12px;
                                    border-left:6px solid #2563eb;
                                    margin-bottom:12px;
                                    box-shadow:0 2px 8px rgba(0,0,0,.1);
                                    ">
                                    <b>{i+1}.</b>
                                    {p['quantifier']} {p['subject']} {p['copula']} {p['predicate']}
                                    </div>
                                    """,unsafe_allow_html=True)
            with col2:
                if st.button("X", key=f"delete_premise_{i}"):
                    st.session_state.premises.pop(i)
                    st.rerun()

# Display Conclusion
with st.expander(" Conclusions", expanded=True):
    if len(st.session_state.conclusions) == 0:
        st.info("No conclusions added.")
    else:
        for i, c in enumerate(st.session_state.conclusions):
            col1, col2 = st.columns([6,1])
            text = f"{c['quantifier']} {c['subject']} {c['copula']} {c['predicate']}"
            if c["modifier"] != "none":
                text += f" {c['modifier']}"
            with col1:
                st.markdown(f"""
                            <div class="conclusion-card" style="
                            background:#ecfdf5;
                            color:#166534;
                            padding:15px;
                            border-radius:12px;
                            border-left:6px solid #16a34a;
                            margin-bottom:12px;
                            box-shadow:0 2px 8px rgba(0,0,0,.1);
                            ">
                            <b>{i+1}.</b>
                            {text}
                            </div>
                            """,unsafe_allow_html=True)
            
            with col2:
                if st.button("X", key=f"delete_conclusion_{i}"):
                    st.session_state.conclusions.pop(i)
                    st.rerun()

#clear the all the premises and conclusions
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🗑 Clear All Premises"):
        st.session_state.premises.clear()
        st.rerun()

with col2:
    if st.button("🗑 Clear All Conclusions"):
        st.session_state.conclusions.clear()
        st.rerun()


st.markdown("<br>", unsafe_allow_html=True)


if st.button("Check Validity"):
    if len(st.session_state.premises) == 0:
        st.warning("Please add at least one premise.")
    elif len(st.session_state.conclusions) == 0:
        st.warning("Please set a conclusion.")
    else:
        results, pair_info = Logic.check(st.session_state.premises, st.session_state.conclusions)

        # Announce each complementary pair once, right under the "Results"
        # heading, instead of repeating "(Complementary Pair)" on every
        # individual result line below.
        for info in pair_info:
            i1 = info["some_index"] + 1
            i2 = info["no_index"] + 1
            st.markdown(f"""
                    <div style="
                    background:#fef9c3;
                    color:#854d0e;
                    padding:10px 15px;
                    border-radius:10px;
                    margin-bottom:10px;
                    border-left:6px solid #eab308;
                    font-size:15px;
                    ">
                    🔗 <b>Conclusion {i1} &amp; Conclusion {i2}</b> form a Complementary Pair
                    ("{info['subject'].title()}" / "{info['predicate'].title()}")
                    </div>
                    """, unsafe_allow_html=True)
       
        # Conclusions that are part of ANY complementary pair (Some X are Y
        # / No X are Y) are pulled out of the normal green/red display
        # below and shown separately in yellow - whether the pair resolved
        # to one side or is genuinely ambiguous ("either ... or ...").
        pair_indices = set()
        for info in pair_info:
            pair_indices.add(info["some_index"])
            pair_indices.add(info["no_index"])

        for i, result in enumerate(results, start=1):
            if (i - 1) in pair_indices:
                continue
            if result:
                 st.markdown(f"""
                        <div style="
                        background:#dcfce7;
                        color:#166534;
                        padding:15px;
                        border-radius:12px;
                        margin-bottom:10px;
                        border-left:6px solid #16a34a;
                        ">
                        <h4 style="margin:0;">🟢 Conclusion {i} follow</h4>
                        </div>
                        """,unsafe_allow_html=True)
            else:
                   st.markdown(f"""
                        <div style="
                        background:#dcfce7;
                        color:#ff0000;
                        padding:15px;
                        border-radius:12px;
                        margin-bottom:10px;
                        border-left:6px solid #16a34a;
                        ">
                        <h4 style="margin:0;">🔴 Conclusion {i} does not Follow</h4>
                        </div>
                        """,unsafe_allow_html=True)

        # Show every complementary pair's result in yellow - either as one
        # combined "Either ... or ..." block (genuinely ambiguous), or as
        # the two individual resolved results. No inline label repeated
        # here, since the pair was already announced once above.
        def _complementary_block(text):
            st.markdown(f"""
                    <div style="
                    background:#fef9c3;
                    color:#854d0e;
                    padding:15px;
                    border-radius:12px;
                    margin-bottom:10px;
                    border-left:6px solid #eab308;
                    ">
                    <h4 style="margin:0;">🟡 {text}</h4>
                    </div>
                    """, unsafe_allow_html=True)

        for info in pair_info:
            i1 = info["some_index"] + 1
            i2 = info["no_index"] + 1

            if info["status"] == "either":
                _complementary_block(f"Either Conclusion {i1} or Conclusion {i2} follows")
            elif info["status"] == "no_definite":
                _complementary_block(f"Conclusion {i1} does not Follow")
                _complementary_block(f"Conclusion {i2} follow")
            elif info["status"] == "some_definite":
                _complementary_block(f"Conclusion {i1} follow")
                _complementary_block(f"Conclusion {i2} does not Follow")
