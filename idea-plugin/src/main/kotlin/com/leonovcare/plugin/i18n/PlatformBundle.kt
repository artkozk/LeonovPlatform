package com.leonovcare.plugin.i18n

import com.intellij.AbstractBundle
import org.jetbrains.annotations.PropertyKey

object PlatformBundle : AbstractBundle("messages.PlatformBundle") {
    fun message(@PropertyKey(resourceBundle = "messages.PlatformBundle") key: String, vararg params: Any): String {
        return getMessage(key, *params)
    }
}
