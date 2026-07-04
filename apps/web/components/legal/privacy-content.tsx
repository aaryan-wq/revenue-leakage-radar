import {
  LegalList,
  LegalSection,
  LegalStrong,
  LegalSubsection,
} from "@/components/legal/legal-section";

export function PrivacyContent() {
  return (
    <div className="space-y-8">
      <LegalSection title="1. Introduction">
        <p>
          Welcome to Paevo. This Privacy Policy explains how Paevo Corp. (&quot;
          <LegalStrong>Paevo</LegalStrong>&quot;, &quot;<LegalStrong>we</LegalStrong>&quot;, &quot;
          <LegalStrong>us</LegalStrong>&quot;, or &quot;<LegalStrong>our</LegalStrong>&quot;) collects,
          uses, shares, and protects information in connection with our website, application, and related
          revenue leakage and billing audit services (collectively, the &quot;
          <LegalStrong>Services</LegalStrong>&quot;).
        </p>
        <p>
          Paevo provides business-to-business (B2B) software designed to help finance teams and operators
          identify pricing drift, billing anomalies, and revenue leakage. By accessing or using our
          Services, you acknowledge that you have read and understand this Privacy Policy.
        </p>
      </LegalSection>

      <LegalSection title="2. Information We Collect">
        <p>
          We collect information that you provide to us directly, information we collect automatically
          when you use our Services, and information from third parties.
        </p>

        <LegalSubsection title="A. Information You Provide Directly">
          <LegalList
            items={[
              <>
                <LegalStrong>Account and Profile Information:</LegalStrong> When you register for an
                account, we collect your name, email address, company name, and login credentials.
              </>,
              <>
                <LegalStrong>Uploaded Business Data:</LegalStrong> To perform revenue and billing audits,
                you may upload data files (such as CSV exports) from your billing, subscription, or CRM
                systems. This data may include customer account names, internal IDs, subscription and
                invoice metadata, pricing catalogs, discount records, and billing amounts.{" "}
                <LegalStrong>Note:</LegalStrong> This information primarily relates to your business
                operations, but to the extent it contains personal information (e.g., individual customer
                names or contact details), we process it as necessary to provide the Services.
              </>,
              <>
                <LegalStrong>Payment and Transaction Information:</LegalStrong> If you purchase a paid
                audit report, we collect transaction details. Payment processing is handled by our
                third-party payment processor (Stripe), meaning we do not directly collect or store full
                credit card numbers.
              </>,
              <>
                <LegalStrong>Communications:</LegalStrong> If you contact our sales or support teams, we
                collect the contents of those communications, your contact details, and any related
                metadata.
              </>,
            ]}
          />
        </LegalSubsection>

        <LegalSubsection title="B. Automatically Collected Information">
          <LegalList
            items={[
              <>
                <LegalStrong>Technical and Usage Data:</LegalStrong> When you visit our website or use
                the platform, we automatically collect data such as your IP address, browser type, device
                identifiers, operating system, pages viewed, features used, and timestamps.
              </>,
              <>
                <LegalStrong>Cookies and Similar Technologies:</LegalStrong> We use strictly necessary
                and basic analytical cookies to authenticate users, remember preferences, and understand
                site performance. We do not use third-party ad-retargeting pixels. You may control cookie
                settings through your browser, though disabling them may impact some functionality of the
                Services.
              </>,
            ]}
          />
        </LegalSubsection>
      </LegalSection>

      <LegalSection title="3. How We Use Information">
        <p>We use the information we collect for the following business and operational purposes:</p>
        <LegalList
          items={[
            <>
              <LegalStrong>Operating the Services:</LegalStrong> To authenticate users, provide the
              platform, process data uploads, and generate free scans or detailed audit reports.
            </>,
            <>
              <LegalStrong>Improving the Services:</LegalStrong> To analyze usage trends, debug errors,
              train our automated normalization systems, and improve the accuracy of our revenue leakage
              models.
            </>,
            <>
              <LegalStrong>Processing Payments:</LegalStrong> To facilitate transactions for paid
              reports and enterprise services.
            </>,
            <>
              <LegalStrong>Customer Support:</LegalStrong> To respond to inquiries, troubleshoot issues,
              and provide technical assistance.
            </>,
            <>
              <LegalStrong>Security and Fraud Prevention:</LegalStrong> To monitor for unauthorized
              access, abuse, and security vulnerabilities.
            </>,
            <>
              <LegalStrong>Communications:</LegalStrong> To send transactional notices (e.g., audit
              completion, account updates, security alerts) and, where legally permitted, to send
              marketing or promotional materials related to Paevo. You may opt out of marketing
              communications at any time.
            </>,
            <>
              <LegalStrong>Legal Compliance:</LegalStrong> To comply with applicable legal obligations
              and enforce our Terms of Service.
            </>,
          ]}
        />
      </LegalSection>

      <LegalSection title="4. How We Share Information">
        <p>
          We do not sell your personal information, nor do we share it with data brokers or third parties
          for cross-context behavioral advertising. We may share information under the following
          circumstances:
        </p>
        <LegalList
          items={[
            <>
              <LegalStrong>Service Providers:</LegalStrong> We share data with trusted third-party
              vendors who provide services on our behalf, such as cloud infrastructure hosting,
              analytics, communications, and payment processing (e.g., Stripe).
            </>,
            <>
              <LegalStrong>With Your Authorization:</LegalStrong> We may share information as explicitly
              instructed or authorized by you.
            </>,
            <>
              <LegalStrong>Business Transfers:</LegalStrong> If Paevo is involved in a merger,
              acquisition, financing, reorganization, or sale of assets, information may be shared or
              transferred as part of that transaction.
            </>,
            <>
              <LegalStrong>Legal and Safety Requirements:</LegalStrong> We may disclose information if
              reasonably necessary to comply with a legal obligation, regulatory request, or valid legal
              process; to enforce our agreements; or to protect the rights, property, or safety of Paevo,
              our users, or others.
            </>,
          ]}
        />
      </LegalSection>

      <LegalSection title="5. Data Retention">
        <p>
          We retain personal information and uploaded business data only for as long as reasonably
          necessary to fulfill the purposes described in this Privacy Policy.
        </p>
        <LegalList
          items={[
            <>
              <LegalStrong>Uploaded Files:</LegalStrong> Raw uploaded CSV files and similar data uploads
              are automatically deleted from our active processing servers immediately after your audit
              report is generated.
            </>,
            <>
              <LegalStrong>Account and Report Information:</LegalStrong> Aggregate reports, outputs, and
              account information are retained for the lifetime of your active account so you may access
              your historical data.
            </>,
            <>
              <LegalStrong>Legal and Transactional Records:</LegalStrong> Retained as required to comply
              with tax, legal, and accounting obligations.
            </>,
          ]}
        />
        <p>When data is no longer needed, we securely delete or de-identify it.</p>
      </LegalSection>

      <LegalSection title="6. Security">
        <p>
          We implement reasonable administrative, technical, and organizational measures to protect the
          information we collect and process. However, no internet transmission or electronic storage
          system is 100% secure. We cannot guarantee absolute security. You are responsible for
          protecting your account credentials and ensuring you have the appropriate rights and security
          clearances to upload your company&apos;s billing or CRM data to our platform.
        </p>
      </LegalSection>

      <LegalSection title="7. International Cross-Border Transfers">
        <p>
          Paevo operates primarily in Canada and the United States. Information we collect may be
          transferred to, stored, and processed in jurisdictions other than the one in which you reside,
          including by our service providers.
        </p>
        <p>
          For users located in the European Economic Area (EEA) or the United Kingdom (UK), your data may
          be transferred outside of your jurisdiction. We ensure appropriate safeguards are in place for
          such transfers. Data Processing Agreements (DPAs) incorporating Standard Contractual Clauses
          (SCCs) are available for our enterprise customers upon request.
        </p>
      </LegalSection>

      <LegalSection title="8. User Rights and Choices">
        <p>
          Depending on your location, you may have certain rights regarding your personal information,
          such as the right to:
        </p>
        <LegalList
          items={[
            "Access the personal information we hold about you.",
            "Request correction of inaccurate or incomplete information.",
            "Request deletion of your personal information or account closure.",
            'Opt out of marketing communications by following the "unsubscribe" link in our emails.',
          ]}
        />
        <p>
          To exercise these rights, or to request the deletion of your account and associated data,
          please contact us at the email address below. We will respond to your request in accordance
          with applicable law.
        </p>
      </LegalSection>

      <LegalSection title="9. Children's Privacy">
        <p>
          Our Services are designed strictly for business professionals and are not directed at children
          under the age of 18. We do not knowingly collect personal information from minors.
        </p>
      </LegalSection>

      <LegalSection title="10. Changes to This Privacy Policy">
        <p>
          We may update this Privacy Policy from time to time to reflect changes in our practices or for
          legal and regulatory reasons. We will post the updated policy on this page and update the
          &quot;Last Updated&quot; date. If we make material changes, we may notify you via email or
          through a notice on the platform.
        </p>
      </LegalSection>

      <LegalSection title="11. Contact Us">
        <p>
          If you have any questions, concerns, or requests regarding this Privacy Policy or our data
          practices, please contact us at:
        </p>
        <p>
          <LegalStrong>Paevo Corp.</LegalStrong>
          <br />
          Email:{" "}
          <a href="mailto:contact@paevo.co" className="text-primary hover:underline">
            contact@paevo.co
          </a>
          <br />
          Address: 17 Tobias Lane, Barrie, ON L9J 0T8
        </p>
      </LegalSection>
    </div>
  );
}
