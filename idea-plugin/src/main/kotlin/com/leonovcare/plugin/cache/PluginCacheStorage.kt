package com.leonovcare.plugin.cache

import com.intellij.openapi.application.PathManager
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.StandardCopyOption

object PluginCacheStorage {

    private const val ROOT_DIR_NAME = "leonovcare-platform-plugin-cache"

    fun readJson(fileName: String): String? {
        val path = filePath(fileName)
        if (!Files.exists(path)) return null
        return runCatching { Files.readString(path) }.getOrNull()
    }

    fun writeJson(fileName: String, json: String): Boolean {
        val target = filePath(fileName)
        val parent = target.parent ?: return false

        return runCatching {
            Files.createDirectories(parent)
            val temp = parent.resolve("${target.fileName}.tmp")
            Files.writeString(temp, json)
            Files.move(temp, target, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE)
            true
        }.getOrElse {
            false
        }
    }

    fun delete(fileName: String) {
        val path = filePath(fileName)
        runCatching { Files.deleteIfExists(path) }
    }

    fun clearAll() {
        val root = rootDir()
        if (!Files.exists(root)) return

        runCatching {
            Files.walk(root).use { stream ->
                stream.sorted(Comparator.reverseOrder()).forEach { path ->
                    runCatching { Files.deleteIfExists(path) }
                }
            }
        }
    }

    private fun filePath(fileName: String): Path {
        val root = rootDir()
        val resolved = root.resolve(fileName).normalize()
        require(resolved.startsWith(root)) { "Unsafe cache file path: $fileName" }
        return resolved
    }

    private fun rootDir(): Path {
        return Path.of(PathManager.getSystemPath(), ROOT_DIR_NAME).normalize()
    }
}
