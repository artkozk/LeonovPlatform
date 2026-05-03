package com.leonovcare.plugin.task

import com.leonovcare.plugin.api.LessonMaterial
import com.leonovcare.plugin.api.TaskDetails

object LessonMaterialFormatter {

    fun buildTaskAndLessonText(details: TaskDetails?, lesson: LessonMaterial?): String {
        if (details == null) return ""
        if (lesson == null) return details.statement.body

        val buffer = StringBuilder()

        buffer.appendLine("=== УРОК ===")
        buffer.appendLine("Модуль: ${lesson.moduleTitle}")
        buffer.appendLine("Урок: ${lesson.title}")
        buffer.appendLine()

        val lessonTheory = lesson.contentMd.trim()
        if (lessonTheory.isNotBlank()) {
            buffer.appendLine("=== ТЕОРИЯ УРОКА ===")
            buffer.appendLine(lessonTheory)
            buffer.appendLine()
        }

        if (lesson.blocks.isNotEmpty()) {
            buffer.appendLine("=== ШАГИ УРОКА ===")
            lesson.blocks.sortedBy { it.position }.forEach { block ->
                buffer.append("[")
                    .append(block.position)
                    .append("] ")
                    .append(block.type.uppercase())
                    .append(" — ")
                    .append(if (block.title.isBlank()) "Без названия" else block.title)
                    .appendLine()

                if (block.taskTitle != null && block.taskTitle.isNotBlank()) {
                    buffer.appendLine("Задача блока: ${block.taskTitle}")
                }

                val blockContent = block.contentMd.trim()
                if (blockContent.isNotBlank()) {
                    buffer.appendLine(blockContent)
                }
                buffer.appendLine()
            }
        }

        buffer.appendLine("=== ТЕКУЩАЯ ЗАДАЧА ===")
        buffer.appendLine(details.title)
        buffer.appendLine()
        buffer.append(details.statement.body.trim())
        buffer.appendLine()

        return buffer.toString()
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
