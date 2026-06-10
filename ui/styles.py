def inject_css(st, client_demo: bool = False):
    client_css = """
            /* Modalità cliente: esperienza più pulita e centrata sulla chat */
            .main .block-container {
                max-width: 1060px;
                padding-top: 1.15rem;
            }

            .bitness-hero {
                margin-bottom: 1.65rem;
            }

            .stChatMessage {
                background: transparent;
            }

            div[data-testid="stChatMessage"] {
                border-radius: 18px;
            }

            div[data-testid="stChatInput"] textarea {
                border-radius: 999px;
            }
    """ if client_demo else """
            .main .block-container {
                max-width: 1240px;
                padding-top: 1.5rem;
            }
    """

    st.markdown(
        f"""
        <style>
            :root {{
                --bitness-blue: #2F2ED8;
                --bitness-navy: #00153D;
                --bitness-teal: #008E98;
                --bitness-gold: #E4C06F;
                --bitness-bg: #F6F8FC;
                --bitness-card: #FFFFFF;
                --bitness-line: rgba(0, 21, 61, 0.09);
                --bitness-text: #00153D;
                --bitness-muted: rgba(0, 21, 61, 0.63);
            }}

            {client_css}

            html, body, [class*="css"] {{
                color: var(--bitness-text);
            }}

            .stApp {{
                background:
                    radial-gradient(circle at top left, rgba(47, 46, 216, 0.08), transparent 32rem),
                    radial-gradient(circle at bottom right, rgba(0, 142, 152, 0.08), transparent 30rem),
                    var(--bitness-bg);
            }}

            section[data-testid="stSidebar"] {{
                background: #F6F8FC;
                border-right: 1px solid var(--bitness-line);
            }}

            .bitness-hero {{
                position: relative;
                overflow: hidden;
                background:
                    radial-gradient(circle at 92% 18%, rgba(228, 192, 111, 0.24), transparent 16rem),
                    radial-gradient(circle at 12% 0%, rgba(0, 142, 152, 0.28), transparent 18rem),
                    linear-gradient(135deg, #00153D 0%, #1F2FB6 58%, #2F2ED8 100%);
                border-radius: 28px;
                padding: clamp(1.7rem, 4vw, 2.65rem);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.14);
                border-bottom: 7px solid var(--bitness-teal);
                box-shadow: 0 22px 55px rgba(0, 21, 61, 0.20);
            }}

            .bitness-hero::after {{
                content: "";
                position: absolute;
                inset: auto -8rem -10rem auto;
                width: 24rem;
                height: 24rem;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.08);
            }}

            .bitness-hero-content {{
                position: relative;
                z-index: 1;
            }}

            .bitness-kicker {{
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                font-size: 0.76rem;
                font-weight: 900;
                letter-spacing: 0.14em;
                text-transform: uppercase;
                color: var(--bitness-gold);
                margin-bottom: 0.55rem;
            }}

            .bitness-kicker::before {{
                content: "";
                display: inline-block;
                width: 0.55rem;
                height: 0.55rem;
                border-radius: 50%;
                background: var(--bitness-teal);
                box-shadow: 0 0 0 4px rgba(0, 142, 152, 0.24);
            }}

            .bitness-title {{
                font-size: clamp(2.1rem, 4.6vw, 3.75rem);
                line-height: 1.02;
                font-weight: 950;
                letter-spacing: -0.055em;
                margin-bottom: 0.85rem;
            }}

            .bitness-subtitle {{
                font-size: clamp(1rem, 1.7vw, 1.12rem);
                line-height: 1.65;
                max-width: 820px;
                color: rgba(255, 255, 255, 0.92);
            }}

            .bitness-pill-row {{
                display: flex;
                flex-wrap: wrap;
                gap: 0.65rem;
                margin-top: 1.25rem;
            }}

            .bitness-pill {{
                background: rgba(255, 255, 255, 0.13);
                border: 1px solid rgba(255, 255, 255, 0.24);
                color: #FFFFFF;
                padding: 0.46rem 0.78rem;
                border-radius: 999px;
                font-size: 0.85rem;
                font-weight: 760;
                backdrop-filter: blur(8px);
            }}

            .demo-card,
            .client-welcome-card {{
                background: rgba(255, 255, 255, 0.92);
                border: 1px solid var(--bitness-line);
                border-radius: 20px;
                padding: 1.05rem 1.15rem;
                box-shadow: 0 12px 30px rgba(0, 21, 61, 0.06);
            }}

            .client-welcome-card {{
                margin: 0.15rem 0 1rem 0;
                padding: 1.25rem 1.35rem;
            }}

            .client-welcome-eyebrow {{
                color: var(--bitness-teal);
                font-weight: 900;
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                margin-bottom: 0.35rem;
            }}

            .client-welcome-title {{
                color: var(--bitness-navy);
                font-size: 1.18rem;
                font-weight: 900;
                margin-bottom: 0.35rem;
            }}

            .client-welcome-text {{
                color: var(--bitness-muted);
                line-height: 1.55;
                font-size: 0.95rem;
            }}

            .section-title {{
                color: var(--bitness-navy);
                font-size: 1.04rem;
                font-weight: 850;
                margin-bottom: 0.4rem;
            }}

            .small-muted {{
                color: var(--bitness-muted);
                font-size: 0.91rem;
                line-height: 1.48;
            }}

            .stButton > button {{
                border-radius: 14px;
                font-weight: 800;
                border: 1px solid var(--bitness-line);
                background: #FFFFFF;
                color: var(--bitness-navy);
                box-shadow: 0 8px 22px rgba(0, 21, 61, 0.045);
            }}

            .stButton > button:hover {{
                border-color: rgba(0, 142, 152, 0.45);
                color: var(--bitness-blue);
            }}

            div[data-testid="stMetric"] {{
                background: #FFFFFF;
                padding: 0.85rem 1rem;
                border-radius: 16px;
                border: 1px solid var(--bitness-line);
                box-shadow: 0 8px 22px rgba(0, 21, 61, 0.05);
            }}

            div[data-testid="stExpander"] {{
                border-radius: 16px;
                border: 1px solid var(--bitness-line);
                overflow: hidden;
                background: rgba(255, 255, 255, 0.92);
            }}

            div[data-testid="stChatMessage"] {{
                border: 1px solid rgba(0, 21, 61, 0.06);
                background: rgba(255, 255, 255, 0.74);
                box-shadow: 0 10px 25px rgba(0, 21, 61, 0.045);
            }}

            div[data-testid="stChatInput"] {{
                background: transparent;
            }}

            div[data-testid="stChatInput"] textarea {{
                border: 1px solid rgba(0, 21, 61, 0.12);
                box-shadow: 0 14px 35px rgba(0, 21, 61, 0.08);
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
