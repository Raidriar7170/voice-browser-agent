CHINESE_FIRST_NORMALIZER_EXAMPLES = [
    {
        "transcript": "打开 GitHub 搜索 browser-use-vision，不要登录",
        "output": {
            "kind": "browser_task_request",
            "intent_type": "search_open",
            "constraints": ["public pages only", "stop if login is required"],
        },
    },
    {
        "transcript": "点击右上角的放大镜图标",
        "output": {
            "kind": "browser_task_request",
            "intent_type": "click_visual_target",
            "visual_references": [{"kind": "icon", "text": "top-right magnifying glass"}],
        },
    },
    {
        "transcript": "打开那个页面",
        "output": {
            "kind": "clarification_request",
            "reason": "ambiguous_target",
        },
    },
]

