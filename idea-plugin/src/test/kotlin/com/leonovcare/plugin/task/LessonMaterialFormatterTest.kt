package com.leonovcare.plugin.task

import com.leonovcare.plugin.api.LessonBlock
import com.leonovcare.plugin.api.LessonMaterial
import com.leonovcare.plugin.api.LessonTaskSummary
import com.leonovcare.plugin.api.StatementFormat
import com.leonovcare.plugin.api.TaskDetails
import com.leonovcare.plugin.api.TaskStatement
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class LessonMaterialFormatterTest {

    @Test
    fun `buildTaskAndLessonText includes lesson theory blocks and task section`() {
        val details = TaskDetails(
            id = "task-1",
            courseId = "course-1",
            title = "Сумма чисел",
            statement = TaskStatement(
                format = StatementFormat.MARKDOWN,
                body = "Напишите программу, которая выводит сумму двух чисел.",
                requirements = listOf("Считать два числа", "Вывести только сумму"),
            ),
            language = "PYTHON",
            type = TaskType.CONSOLE,
            templateVersion = "1",
            entryPoint = "main.py",
            mainFilePath = "main.py",
        )
        val lesson = LessonMaterial(
            id = "lesson-1",
            title = "Переменные",
            moduleTitle = "Базовый Python",
            position = 1,
            contentMd = "Переменные помогают хранить значения.",
            tasks = listOf(
                LessonTaskSummary(
                    id = "task-1",
                    title = "Сумма чисел",
                    type = TaskType.CONSOLE,
                    language = "PYTHON",
                )
            ),
            blocks = listOf(
                LessonBlock(
                    id = "block-1",
                    type = "theory",
                    title = "Что такое переменная",
                    contentMd = "Переменная имеет имя и значение.",
                    position = 1,
                )
            ),
        )

        val output = LessonMaterialFormatter.buildTaskAndLessonText(details, lesson)

        assertTrue(output.contains("# Переменные"))
        assertTrue(output.contains("## Теория"))
        assertTrue(output.contains("## Шаги урока"))
        assertTrue(output.contains("## Практическое задание: Сумма чисел"))
        assertTrue(output.contains("### Что нужно сделать"))
    }

    @Test
    fun `buildTaskAndLessonText returns task section when lesson is absent`() {
        val details = TaskDetails(
            id = "task-1",
            courseId = "course-1",
            title = "Hello",
            statement = TaskStatement(
                format = StatementFormat.MARKDOWN,
                body = "Выведите Hello, World!",
            ),
            language = "PYTHON",
            type = TaskType.CONSOLE,
            templateVersion = "1",
            entryPoint = "main.py",
            mainFilePath = "main.py",
        )

        val output = LessonMaterialFormatter.buildTaskAndLessonText(details, lesson = null)

        assertTrue(output.contains("## Практическое задание: Hello"))
        assertTrue(output.contains("Выведите Hello, World!"))
    }
}
