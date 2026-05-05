package com.leonovcare.plugin.task

import com.leonovcare.plugin.api.LessonMaterial
import com.leonovcare.plugin.api.TaskDetails

object LessonMaterialFormatter {

    fun buildTaskAndLessonText(details: TaskDetails?, lesson: LessonMaterial?): String {
        if (details == null) return ""
        if (lesson == null) return details.statement.body.trim()

        val buffer = StringBuilder()
        val moduleTitle = lesson.moduleTitle.trim()
        val lessonTitle = lesson.title.trim()
        if (moduleTitle.isNotBlank()) {
            buffer.appendLine("**Модуль:** $moduleTitle")
        }
        if (lessonTitle.isNotBlank()) {
            buffer.appendLine("**Урок:** $lessonTitle")
        }
        if (buffer.isNotEmpty()) {
            buffer.appendLine()
            buffer.appendLine("---")
            buffer.appendLine()
        }

        val statement = details.statement.body.trim()
        if (statement.isNotBlank()) {
            buffer.appendLine(statement)
        }
        return buffer.toString().trim()
    }

    fun buildLessonMarkdown(lesson: LessonMaterial): String {
        val buffer = StringBuilder()
        buffer.appendLine("# ${lesson.title}")
        if (lesson.moduleTitle.isNotBlank()) {
            buffer.appendLine()
            buffer.appendLine("**Модуль:** ${lesson.moduleTitle}")
        }

        val lessonTheory = lesson.contentMd.trim()
        if (lessonTheory.isNotBlank()) {
            buffer.appendLine()
            buffer.appendLine("## Теория")
            buffer.appendLine()
            buffer.appendLine(lessonTheory)
        }

        if (lesson.blocks.isNotEmpty()) {
            buffer.appendLine()
            buffer.appendLine("## Шаги урока")
            lesson.blocks.sortedBy { it.position }.forEach { block ->
                buffer.appendLine()
                buffer.appendLine("### ${block.position}. ${block.title.ifBlank { block.type }}")
                buffer.appendLine()
                buffer.appendLine("_Тип: ${block.type}_")

                if (block.taskTitle != null && block.taskTitle.isNotBlank()) {
                    buffer.appendLine()
                    buffer.appendLine("**Задача:** ${block.taskTitle}")
                }

                val blockContent = block.contentMd.trim()
                if (blockContent.isNotBlank()) {
                    buffer.appendLine()
                    buffer.appendLine(blockContent)
                }
            }
        }
        return buffer.toString().trim() + "\n"
    }
}
