package com.leonovcare.plugin.task

import com.leonovcare.plugin.api.LessonMaterial
import com.leonovcare.plugin.api.TaskDetails

object LessonMaterialFormatter {

    fun buildTaskAndLessonText(details: TaskDetails?, lesson: LessonMaterial?): String {
        if (details == null) return ""
        val sections = mutableListOf<String>()

        if (lesson != null) {
            val lessonMarkdown = buildLessonMarkdown(lesson).trim()
            if (lessonMarkdown.isNotBlank()) {
                sections += lessonMarkdown
            }
        }

        val taskSection = StringBuilder()
        val taskTitle = details.title.trim()
        if (taskTitle.isNotBlank()) {
            taskSection.appendLine("## Практическое задание: $taskTitle")
        } else {
            taskSection.appendLine("## Практическое задание")
        }

        val statement = details.statement.body.trim()
        if (statement.isNotBlank()) {
            taskSection.appendLine()
            taskSection.appendLine(statement)
        }

        val requirements = details.statement.requirements
            .map { it.trim() }
            .filter { it.isNotBlank() }
        if (requirements.isNotEmpty()) {
            taskSection.appendLine()
            taskSection.appendLine("### Что нужно сделать")
            requirements.forEachIndexed { index, item ->
                taskSection.appendLine("${index + 1}. $item")
            }
        }

        sections += taskSection.toString().trim()
        return sections.joinToString("\n\n---\n\n").trim()
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
