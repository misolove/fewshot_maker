import streamlit as st
from classes import Data
import tiktoken
from typing import List, Dict, Any
from random import randint
from classes import IdCounter
from interface import render, display_result_prompt

def session_state_init() -> None:
    if "examples" not in st.session_state:
        st.session_state.examples = []
    if "id_counter" not in st.session_state:
        st.session_state.id_counter = IdCounter()

def combine_prompt(data: Data, examples: List[Dict[str, Any]] = None) -> str:
    prompt = data.get("prompt")
    requirements = data.get("requirements")
    constraints = data.get("constraints")
    count_generation = data.get("count_generation")
    prompt = prompt.replace("{{requirements}}", requirements) if requirements else prompt.replace("{{requirements}}", "None")
    prompt = prompt.replace("{{constraints}}", constraints) if constraints else prompt.replace("{{constraints}}", "None")
    prompt = prompt.replace("{{count_generation}}", str(count_generation))
    return prompt

def postprocess(data: Data) -> Data:
    prompt = combine_prompt(data)
    enc = tiktoken.encoding_for_model("gpt-4o-mini")
    token_count = len(enc.encode(prompt))
    data.set("result_prompt", prompt)
    data.set("token_count", token_count)
    return data

def update_interface(data: Data) -> None:
    data.get("count_notice").text(f"생성시 필요 토큰 개수: {data.get('token_count')}")
    cost = data.get("token_count") * 0.000005
    data.get("cost_notice").text(f"생성 비용: {cost:.5f} 달러")
    if data.get("example_append"):
        if data.get("user_input").get() and data.get("assistant_output").get():
            st.session_state.examples.append({
                "id": st.session_state.id_counter.get(),
                "user_input": data.get("user_input").get(),
                "assistant_output": data.get("assistant_output").get(),
            })
            data.get("user_input").clear()
            data.get("assistant_output").clear()
            data.get("example_addition_notice").success("예제 추가 성공")
            st.rerun()
        else:
            data.get("example_addition_notice").error("예제 추가 실패")

    display_result_prompt(data.get("result_prompt"), data.get("result_display_asset"))

def run_impl() -> None:
    st.set_page_config(layout="wide")
    session_state_init()
    data = render()
    postprocessed = postprocess(data)
    update_interface(postprocessed)

class MainController:
    @staticmethod
    def run() -> None:
        run_impl()
