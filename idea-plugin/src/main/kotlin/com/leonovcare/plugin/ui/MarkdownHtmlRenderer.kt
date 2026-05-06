package com.leonovcare.plugin.ui

import com.intellij.openapi.util.text.StringUtil

object MarkdownHtmlRenderer {

    private val headingRegex = Regex("^(#{1,6})\\s+(.+)$")
    private val orderedListRegex = Regex("^\\d+\\.\\s+(.+)$")
    private val unorderedListRegex = Regex("^[-*]\\s+(.+)$")
    private val boldRegex = Regex("\\*\\*(.+?)\\*\\*")
    private val inlineCodeRegex = Regex("`([^`]+)`")

    fun render(
        markdown: String,
        textColorHex: String = "#d8dee9",
        backgroundColorHex: String = "#2b2d30",
    ): String {
        val source = markdown.replace("\r\n", "\n").replace("\r", "\n").trim()
        if (source.isBlank()) {
            return htmlDocument(
                body = "<p class='muted'>Нет материалов для отображения.</p>",
                textColorHex = textColorHex,
                backgroundColorHex = backgroundColorHex,
            )
        }

        val html = StringBuilder()
        val paragraph = mutableListOf<String>()
        var inCodeBlock = false
        var inUnorderedList = false
        var inOrderedList = false

        fun flushParagraph() {
            if (paragraph.isEmpty()) return
            val text = paragraph.joinToString(" ").trim()
            if (text.isNotBlank()) {
                html.append("<p>").append(formatInline(text)).append("</p>")
            }
            paragraph.clear()
        }

        fun closeLists() {
            if (inUnorderedList) {
                html.append("</ul>")
                inUnorderedList = false
            }
            if (inOrderedList) {
                html.append("</ol>")
                inOrderedList = false
            }
        }

        for (raw in source.split('\n')) {
            val line = raw.trimEnd()
            val trimmed = line.trim()

            if (trimmed.startsWith("```")) {
                flushParagraph()
                closeLists()
                if (inCodeBlock) {
                    html.append("</code></pre>")
                    inCodeBlock = false
                } else {
                    html.append("<pre><code>")
                    inCodeBlock = true
                }
                continue
            }

            if (inCodeBlock) {
                html.append(StringUtil.escapeXmlEntities(line)).append('\n')
                continue
            }

            if (trimmed.isBlank()) {
                flushParagraph()
                closeLists()
                continue
            }

            val headingMatch = headingRegex.matchEntire(trimmed)
            if (headingMatch != null) {
                flushParagraph()
                closeLists()
                val level = headingMatch.groupValues[1].length
                val headingText = formatInline(headingMatch.groupValues[2].trim())
                html.append("<h").append(level).append(">").append(headingText).append("</h").append(level).append(">")
                continue
            }

            if (trimmed.startsWith("> ")) {
                flushParagraph()
                closeLists()
                html.append("<blockquote>").append(formatInline(trimmed.removePrefix("> ").trim())).append("</blockquote>")
                continue
            }

            val unorderedMatch = unorderedListRegex.matchEntire(trimmed)
            if (unorderedMatch != null) {
                flushParagraph()
                if (inOrderedList) {
                    html.append("</ol>")
                    inOrderedList = false
                }
                if (!inUnorderedList) {
                    html.append("<ul>")
                    inUnorderedList = true
                }
                html.append("<li>").append(formatInline(unorderedMatch.groupValues[1].trim())).append("</li>")
                continue
            }

            val orderedMatch = orderedListRegex.matchEntire(trimmed)
            if (orderedMatch != null) {
                flushParagraph()
                if (inUnorderedList) {
                    html.append("</ul>")
                    inUnorderedList = false
                }
                if (!inOrderedList) {
                    html.append("<ol>")
                    inOrderedList = true
                }
                html.append("<li>").append(formatInline(orderedMatch.groupValues[1].trim())).append("</li>")
                continue
            }

            paragraph += trimmed
        }

        flushParagraph()
        closeLists()
        if (inCodeBlock) {
            html.append("</code></pre>")
        }

        return htmlDocument(
            body = html.toString(),
            textColorHex = textColorHex,
            backgroundColorHex = backgroundColorHex,
        )
    }

    private fun formatInline(value: String): String {
        var escaped = StringUtil.escapeXmlEntities(value)
        escaped = boldRegex.replace(escaped) { "<strong>${it.groupValues[1]}</strong>" }
        escaped = inlineCodeRegex.replace(escaped) { "<code>${it.groupValues[1]}</code>" }
        return escaped
    }

    private fun htmlDocument(
        body: String,
        textColorHex: String,
        backgroundColorHex: String,
    ): String {
        val quoteBackgroundHex = "#3a3d42"
        val codeBackgroundHex = "#3f434a"
        val mutedTextHex = "#9ba3af"
        return """
            <html>
            <head>
              <style>
                body {
                  font-family: "Segoe UI", "Noto Sans", sans-serif;
                  font-size: 13px;
                  line-height: 1.45;
                  margin: 10px;
                  color: $textColorHex;
                  background-color: $backgroundColorHex;
                }
                h1, h2, h3, h4, h5, h6 { margin: 12px 0 6px; }
                p { margin: 6px 0; }
                ul, ol { margin: 6px 0 8px 18px; padding: 0; }
                blockquote { margin: 8px 0; padding: 6px 10px; border-left: 3px solid #6c7380; background-color: $quoteBackgroundHex; }
                code { font-family: Consolas, "JetBrains Mono", monospace; background-color: $codeBackgroundHex; padding: 1px 4px; }
                pre { font-family: Consolas, "JetBrains Mono", monospace; background-color: $codeBackgroundHex; padding: 10px; white-space: pre; }
                pre code { background-color: $codeBackgroundHex; padding: 0; }
                .muted { color: $mutedTextHex; }
              </style>
            </head>
            <body>$body</body>
            </html>
        """.trimIndent()
    }
}
