import { Check } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { applyPromoCode, cancelSubscription, checkout, plans, subscription, subscriptionPaymentStatus } from "../api/client";

type PlanItem = {
  code: string;
  title: string;
  description: string;
  priceRub: number;
  dailySubmissionLimit: number;
  maxCourses?: number | null;
};

type SubscriptionState = {
  code: string;
  status: string;
  endsAt?: string | null;
  autoRenew?: boolean;
};

type PaymentState = {
  paymentId: string;
  provider: string;
  providerBill: string;
  status: string;
  terminal: boolean;
  canRetry: boolean;
  checkoutUrl: string;
  amountRub: number;
  planCode: string;
  planTitle: string;
  createdAt: string;
  updatedAt: string;
};

const featureMap: Record<string, string[]> = {
  pro: [
    "Доступ к 1 курсу",
    "Практика и автопроверка заданий",
    "Полный доступ к материалам выбранного курса",
  ],
  premium: [
    "Доступ ко всем курсам",
    "AI-подсказки в задачах",
    "Максимальный лимит отправок и приоритет проверки",
  ],
};

const TECHNICAL_FREE_PLAN_CODE = "free";

function planLabel(code?: string | null) {
  const value = String(code ?? "").trim().toLowerCase();
  if (value === TECHNICAL_FREE_PLAN_CODE || value === "") return "Без подписки";
  if (value === "pro") return "Start";
  if (value === "premium") return "Premium";
  return value.toUpperCase();
}

function humanPaymentStatus(status: string) {
  const value = String(status ?? "").toLowerCase();
  if (value === "paid") return "Оплачен";
  if (value === "pending") return "Ожидает оплаты";
  if (value === "processing") return "Обработка";
  if (value === "underpaid") return "Недоплата";
  if (value === "provider_error") return "Ошибка провайдера";
  if (value === "failed") return "Неуспешно";
  if (value === "refunded" || value === "reversed" || value === "chargeback") return "Платеж отозван";
  if (value === "pending_config") return "Ожидает настройки";
  return status || "Неизвестно";
}

function formatCheckoutError(e: any) {
  const payload = e?.response?.data ?? {};
  const apiError = String(payload?.error ?? "").trim();
  const apiDetails = String(payload?.details ?? "").trim();
  const missingRaw = payload?.missing;
  const missing = Array.isArray(missingRaw) ? missingRaw.map((item) => String(item).trim()).filter(Boolean) : [];

  if (apiError === "payment provider is not configured") {
    const missingText = missing.length > 0 ? ` Требуется заполнить: ${missing.join(", ")}.` : "";
    return `Оплата временно недоступна. ${apiDetails || "Платежный провайдер не готов к checkout."}${missingText}`.trim();
  }
  if (apiError && apiDetails) {
    return `${apiError}. ${apiDetails}`;
  }
  if (apiError) {
    return apiError;
  }
  return "Ошибка создания платёжной сессии.";
}

export function BillingPage() {
  const [searchParams] = useSearchParams();
  const [planItems, setPlanItems] = useState<PlanItem[]>([]);
  const [current, setCurrent] = useState<SubscriptionState | null>(null);
  const [paymentState, setPaymentState] = useState<PaymentState | null>(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [promoCode, setPromoCode] = useState("");
  const [promoLoading, setPromoLoading] = useState(false);

  const pendingPayment = searchParams.get("pendingPayment") ?? "";
  const featuredPlan = useMemo(() => planItems.find((plan) => plan.code === "premium")?.code ?? "premium", [planItems]);

  async function load() {
    try {
      const [p, s] = await Promise.all([plans(), subscription()]);
      setPlanItems((p ?? []) as PlanItem[]);
      setCurrent((s ?? null) as SubscriptionState | null);
    } catch (e: any) {
      setMessage(e?.response?.data?.error ?? "Не удалось загрузить тарифы.");
    }
  }

  async function loadPaymentStatus(paymentId: string, sync = true) {
    const response = await subscriptionPaymentStatus(paymentId, sync);
    const payment = (response?.payment ?? null) as PaymentState | null;
    const sub = (response?.subscription ?? null) as SubscriptionState | null;
    if (payment) {
      setPaymentState(payment);
    }
    if (sub) {
      setCurrent(sub);
    }
    return payment;
  }

  useEffect(() => {
    void load();
  }, []);

  useEffect(() => {
    if (!pendingPayment) {
      setPaymentState(null);
      return;
    }

    let stopped = false;
    let timer: ReturnType<typeof setTimeout> | null = null;
    let attempts = 0;

    const poll = async () => {
      attempts += 1;
      try {
        const payment = await loadPaymentStatus(pendingPayment, true);
        if (!payment) {
          setMessage(`Платёж ${pendingPayment} не найден.`);
          return;
        }

        if (payment.status === "paid") {
          setMessage(`Оплата подтверждена: ${payment.planTitle}. Подписка активирована.`);
          return;
        }
        if (payment.status === "failed" || payment.status === "provider_error") {
          setMessage("Оплата не прошла. Можно создать новый checkout.");
          return;
        }
        if (payment.status === "underpaid") {
          setMessage("Платеж зафиксирован как недоплата. Требуется повторная оплата.");
          return;
        }
        if (payment.terminal || attempts >= 18) {
          setMessage(`Статус платежа: ${humanPaymentStatus(payment.status)}.`);
          return;
        }
      } catch (e: any) {
        setMessage(e?.response?.data?.error ?? "Не удалось получить статус платежа.");
      }

      if (!stopped) {
        timer = setTimeout(poll, 5000);
      }
    };

    void poll();
    return () => {
      stopped = true;
      if (timer) {
        clearTimeout(timer);
      }
    };
  }, [pendingPayment]);

  async function onCheckout(planCode: string) {
    setLoading(true);
    try {
      const result = await checkout(planCode);
      if (result.status === "pending_config") {
        setPaymentState({
          paymentId: result.paymentId,
          provider: "cardlink",
          providerBill: "",
          status: "pending_config",
          terminal: false,
          canRetry: true,
          checkoutUrl: result.checkoutUrl,
          amountRub: 0,
          planCode,
          planTitle: planCode.toUpperCase(),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        });
        setMessage(`Платёж создан (${result.paymentId}), но Cardlink пока не настроен в production.`);
        return;
      }

      setMessage("Checkout создан. Открываем страницу оплаты.");
      setPaymentState({
        paymentId: result.paymentId,
        provider: "cardlink",
        providerBill: "",
        status: result.status ?? "pending",
        terminal: false,
        canRetry: false,
        checkoutUrl: result.checkoutUrl,
        amountRub: 0,
        planCode,
        planTitle: planCode.toUpperCase(),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      });
      window.open(result.checkoutUrl, "_blank", "noopener,noreferrer");
      void loadPaymentStatus(result.paymentId, true);
    } catch (e: any) {
      setMessage(formatCheckoutError(e));
    } finally {
      setLoading(false);
    }
  }

  async function onCancel() {
    setLoading(true);
    try {
      const result = await cancelSubscription();
      if (result?.status === "cancel_at_period_end") {
        setMessage("Автопродление отключено. Доступ сохранён до конца оплаченного периода.");
      } else {
        setMessage("Подписка обновлена.");
      }
      await load();
    } catch (e: any) {
      setMessage(e?.response?.data?.error ?? "Не удалось отменить подписку.");
    } finally {
      setLoading(false);
    }
  }

  async function onApplyPromo() {
    const normalized = promoCode.trim().toUpperCase();
    if (!normalized) {
      setMessage("Введите промокод.");
      return;
    }
    setPromoLoading(true);
    setMessage("");
    try {
      const result = await applyPromoCode(normalized);
      setPromoCode("");
      setMessage(`Промокод ${result?.code ?? normalized} активирован. План: ${planLabel(result?.planCode)}.`);
      await load();
    } catch (e: any) {
      setMessage(e?.response?.data?.error ?? "Не удалось применить промокод.");
    } finally {
      setPromoLoading(false);
    }
  }

  return (
    <div className="billing-page page-stack">
      <section className="surface">
        <div className="page-title-block">
          <h1>Подписка</h1>
          <p>Доступ к материалам открыт только с активной подпиской.</p>
        </div>

        <div className="subscription-summary">
          <span className="badge badge-blue">Текущий план: {planLabel(current?.code)}</span>
          <span className="badge badge-neutral">Статус: {current?.status ?? "active"}</span>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={onCancel}
            disabled={loading || (current?.code ?? TECHNICAL_FREE_PLAN_CODE) === TECHNICAL_FREE_PLAN_CODE}
          >
            Отключить автопродление
          </button>
        </div>

        {(current?.code ?? TECHNICAL_FREE_PLAN_CODE) === TECHNICAL_FREE_PLAN_CODE && (
          <div className="status-box status-box-error">
            Без подписки доступ к курсам и заданиям закрыт.
          </div>
        )}
      </section>

      <section className="surface">
        <div className="section-head">
          <div>
            <h2>Промокод</h2>
            <p>Одноразовый код для тестовой активации подписки без оплаты.</p>
          </div>
        </div>
        <div className="subscription-summary">
          <input
            type="text"
            className="input"
            placeholder="Введите 12-символьный промокод"
            value={promoCode}
            onChange={(event) => setPromoCode(event.target.value)}
            maxLength={32}
            autoComplete="off"
          />
          <button type="button" className="btn btn-primary btn-sm" onClick={onApplyPromo} disabled={promoLoading}>
            {promoLoading ? "Применяем..." : "Применить промокод"}
          </button>
        </div>
      </section>

      {paymentState && (
        <section className="surface">
          <div className="section-head">
            <div>
              <h2>Текущий платёж</h2>
              <p>Идентификатор: {paymentState.paymentId}</p>
            </div>
            <span className="badge badge-neutral">{humanPaymentStatus(paymentState.status)}</span>
          </div>
          <p className="text-muted">
            План: {paymentState.planCode.toUpperCase()}
            {paymentState.providerBill ? ` • Bill: ${paymentState.providerBill}` : ""}
          </p>
          {paymentState.checkoutUrl && !paymentState.terminal && (
            <button type="button" className="btn btn-secondary btn-sm" onClick={() => window.open(paymentState.checkoutUrl, "_blank", "noopener,noreferrer")}>
              Открыть checkout
            </button>
          )}
        </section>
      )}

      <section className="pricing-grid">
        {planItems.map((plan) => {
          const isCurrent = current?.code === plan.code;
          const isFeatured = plan.code === featuredPlan;
          const features = featureMap[plan.code] ?? [
            plan.maxCourses && plan.maxCourses > 0 ? `Доступ к ${plan.maxCourses} курсу(ам)` : "Доступ ко всем курсам",
            "Практика задач",
            `Лимит отправок: ${plan.dailySubmissionLimit} в день`,
          ];

          return (
            <article key={plan.code} className={`surface pricing-card ${isFeatured ? "featured" : ""}`}>
              <div className="pricing-head">
                <h2>{plan.title}</h2>
                {isFeatured && <span className="badge badge-purple">Рекомендуем</span>}
              </div>

              <p className="pricing-description">{plan.description}</p>
              <div className="pricing-price">{plan.priceRub} ₽ <span>/ месяц</span></div>
              <p className="pricing-limit">
                {plan.maxCourses && plan.maxCourses > 0 ? `Доступно курсов: ${plan.maxCourses}` : "Доступно курсов: все"}
              </p>
              <p className="pricing-limit">Лимит отправок: {plan.dailySubmissionLimit} в день</p>

              <ul className="pricing-features">
                {features.map((feature) => (
                  <li key={feature}>
                    <Check size={14} strokeWidth={2.4} />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                type="button"
                className={`btn ${isFeatured ? "btn-primary" : "btn-secondary"}`}
                onClick={() => onCheckout(plan.code)}
                disabled={loading || isCurrent}
              >
                {isCurrent ? "Текущий тариф" : "Оформить подписку"}
              </button>
            </article>
          );
        })}
      </section>

      {message && <div className="status-box">{message}</div>}
    </div>
  );
}
