export type ConsentType =
  | "offer"
  | "privacy"
  | "personal_data"
  | "rules"
  | "product_addendum"
  | "autopay"
  | "ads"
  | "cookies";

export type ConsentItem = {
  type: ConsentType;
  required: boolean | "only_when_recurring";
  defaultChecked: false;
  label: string;
  href: string;
  document: string;
  version: string;
  evidenceToStore: string[];
};

export const REGISTRATION_CONSENTS: ConsentItem[] = [
  {
    type: "privacy",
    required: true,
    defaultChecked: false,
    label: "I have read the Privacy and Personal Data Policy.",
    href: "/legal/privacy",
    document: "Privacy Policy",
    version: "[VERSION]",
    evidenceToStore: ["userId", "version", "timestamp", "source"],
  },
  {
    type: "personal_data",
    required: true,
    defaultChecked: false,
    label: "I consent to personal-data processing for registration and service access.",
    href: "/legal/personal-data-consent",
    document: "Personal Data Consent",
    version: "[VERSION]",
    evidenceToStore: ["userId", "version", "timestamp", "source", "labelHash"],
  },
  {
    type: "ads",
    required: false,
    defaultChecked: false,
    label: "I agree to receive advertising and informational messages.",
    href: "/legal/advertising-consent",
    document: "Advertising Consent",
    version: "[VERSION]",
    evidenceToStore: ["userId", "version", "timestamp", "source", "labelHash"],
  },
];

export const PAYMENT_CONSENTS: ConsentItem[] = [
  {
    type: "offer",
    required: true,
    defaultChecked: false,
    label: "I accept the Public Offer.",
    href: "/legal/offer",
    document: "Public Offer",
    version: "[VERSION]",
    evidenceToStore: ["userId", "orderId", "version", "timestamp", "source"],
  },
  {
    type: "autopay",
    required: "only_when_recurring",
    defaultChecked: false,
    label: "I agree to recurring charges under the subscription terms.",
    href: "/legal/autopay-consent",
    document: "Autopay Consent",
    version: "[VERSION]",
    evidenceToStore: ["userId", "orderId", "amount", "period", "version", "timestamp", "source"],
  },
];
