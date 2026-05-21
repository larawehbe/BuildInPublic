"""LangChain chat plumbing: prompt assembly and message-history conversion."""

from __future__ import annotations

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from prompts import SYSTEM_PROMPT_BASE, SYSTEM_PROMPT_RAG_SUFFIX


def build_prompt(pdf_context: str | None) -> ChatPromptTemplate:
    system = SYSTEM_PROMPT_BASE
    if pdf_context:
        system += SYSTEM_PROMPT_RAG_SUFFIX.format(pdf_context=pdf_context)
    return ChatPromptTemplate.from_messages([
        ("system", system),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])


def messages_to_history(messages) -> list[BaseMessage]:
    return [
        HumanMessage(content=m.content) if m.role == "user"
        else AIMessage(content=m.content)
        for m in messages
    ]
