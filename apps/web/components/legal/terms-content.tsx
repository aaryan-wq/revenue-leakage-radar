import {
  LegalList,
  LegalOrderedList,
  LegalSection,
  LegalStrong,
} from "@/components/legal/legal-section";

export function TermsContent() {
  return (
    <div className="space-y-8">
      <LegalSection title="1. Acceptance of Terms">
        <p>
          These Terms of Service (&quot;<LegalStrong>Terms</LegalStrong>&quot;) constitute a legally
          binding agreement between you (and the business or organization you represent) (&quot;
          <LegalStrong>Customer</LegalStrong>&quot;, &quot;<LegalStrong>you</LegalStrong>&quot;, or
          &quot;<LegalStrong>your</LegalStrong>&quot;) and Paevo Corp. (&quot;
          <LegalStrong>Paevo</LegalStrong>&quot;, &quot;<LegalStrong>we</LegalStrong>&quot;, &quot;
          <LegalStrong>us</LegalStrong>&quot;, or &quot;<LegalStrong>our</LegalStrong>&quot;). These
          Terms govern your access to and use of the Paevo website, software platform, and any related
          revenue leakage and billing analysis services (collectively, the &quot;
          <LegalStrong>Services</LegalStrong>&quot;).
        </p>
        <p>
          By creating an account, uploading data, purchasing a report, or otherwise accessing the
          Services, you agree to be bound by these Terms. If you do not agree, you may not use the
          Services.
        </p>
      </LegalSection>

      <LegalSection title="2. Eligibility and Business Use">
        <p>The Services are intended solely for business-to-business (B2B) use. By using the Services, you represent and warrant that:</p>
        <LegalOrderedList
          items={[
            "You are at least 18 years old.",
            "You are using the Services on behalf of a business entity.",
            "You have the legal authority to bind that business entity to these Terms.",
            "You have the necessary permissions, rights, and authority to upload the data files you provide to the Services.",
          ]}
        />
      </LegalSection>

      <LegalSection title="3. Accounts and Access">
        <p>
          While you may be able to run a preliminary free scan without an account, certain
          features, such as accessing detailed paid reports or saving historical data, require account
          registration.
        </p>
        <LegalList
          items={[
            <>
              <LegalStrong>Security:</LegalStrong> You are responsible for maintaining the
              confidentiality of your login credentials and for all activities that occur under your
              account.
            </>,
            <>
              <LegalStrong>Suspension:</LegalStrong> We reserve the right to suspend or terminate your
              account at any time if we suspect unauthorized access, fraud, violation of these Terms,
              or other activities that may threaten the security or integrity of the Services.
            </>,
          ]}
        />
      </LegalSection>

      <LegalSection title="4. Customer Data and Uploaded Files">
        <p>
          To provide the Services, Paevo allows you to upload business data, such as CSV exports from
          billing, subscription, or CRM systems (&quot;<LegalStrong>Customer Data</LegalStrong>&quot;).
        </p>
        <LegalList
          items={[
            <>
              <LegalStrong>Ownership:</LegalStrong> You retain all right, title, and interest in and
              to your Customer Data.
            </>,
            <>
              <LegalStrong>License to Paevo:</LegalStrong> You grant Paevo a limited, non-exclusive,
              worldwide, royalty-free license to host, process, analyze, transmit, store, display, and
              generate outputs from your Customer Data solely as necessary to provide, maintain, and
              improve the Services.
            </>,
            <>
              <LegalStrong>Responsibility:</LegalStrong> You are solely responsible for the accuracy,
              legality, and completeness of your Customer Data. You represent and warrant that your
              uploading and our processing of the Customer Data does not violate any third-party
              rights, confidentiality obligations, or privacy laws.
            </>,
            <>
              <LegalStrong>Aggregated and De-Identified Data:</LegalStrong> Paevo may generate
              de-identified, anonymized, and aggregated usage data, analytics, and benchmarking derived
              from Customer Data. You agree that Paevo may use this aggregated data to train our
              algorithms, build industry benchmarks, and improve our products and services, provided that
              such data cannot reasonably be used to identify you, your company, or any individual.
            </>,
          ]}
        />
      </LegalSection>

      <LegalSection title="5. Acceptable Use">
        <p>You agree not to use the Services to:</p>
        <LegalList
          items={[
            "Violate any applicable local, state, national, or international law.",
            "Upload any Customer Data that you do not have the lawful right to process and share.",
            "Upload malicious code, viruses, or materials that could harm our systems.",
            "Attempt to reverse engineer, decompile, hack, scrape, or otherwise bypass the security or rate limits of the Services.",
            "Build a competitive product or service by abusively extracting data, methodologies, or analytical frameworks from the Services.",
          ]}
        />
      </LegalSection>

      <LegalSection title="6. Audit Outputs and Disclaimers (Important)">
        <p>
          Paevo analyzes your Customer Data using deterministic rules, automated systems, and
          AI-assisted normalization to generate findings, summaries, and reports (&quot;
          <LegalStrong>Outputs</LegalStrong>&quot;). <LegalStrong>Please read the following carefully:</LegalStrong>
        </p>
        <LegalList
          items={[
            <>
              <LegalStrong>Estimates and Assumptions:</LegalStrong> Outputs are software-generated
              estimates based on the data you upload and the assumptions built into our models.
            </>,
            <>
              <LegalStrong>Imperfections:</LegalStrong> Paevo does not guarantee perfect accuracy.
              Outputs may contain errors, omissions, false positives, false negatives, or incomplete
              findings. We do not guarantee that our platform will identify all revenue leakage, pricing
              drift, or billing anomalies.
            </>,
            <>
              <LegalStrong>Informational Purposes Only:</LegalStrong> The Services and Outputs are
              provided strictly for informational and operational decision-support purposes.
            </>,
            <>
              <LegalStrong>No Professional Advice:</LegalStrong> Paevo is not a law firm, accounting
              firm, tax advisor, or fiduciary. The Services do not constitute legal, tax, accounting,
              audit, or financial advice. You are solely responsible for reviewing the findings,
              independently verifying them, and determining what business or financial actions to take.
            </>,
          ]}
        />
      </LegalSection>

      <LegalSection title="7. Fees and Payment">
        <LegalList
          items={[
            <>
              <LegalStrong>Free Scans:</LegalStrong> Paevo may offer free preliminary scans or limited
              features at its sole discretion, which may be modified or discontinued at any time.
            </>,
            <>
              <LegalStrong>Paid Reports:</LegalStrong> Detailed audit reports and premium features are
              subject to payment of specified fees. Prices are subject to change prospectively upon
              notice.
            </>,
            <>
              <LegalStrong>Payment Processing:</LegalStrong> Payments are processed securely via our
              third-party payment processor, Stripe. You agree to provide accurate billing and payment
              information.
            </>,
            <>
              <LegalStrong>Taxes:</LegalStrong> You are responsible for paying any applicable sales,
              use, or value-added taxes associated with your purchase, excluding taxes based on
              Paevo&apos;s net income.
            </>,
            <>
              <LegalStrong>Refunds:</LegalStrong> All sales of paid audit reports are generally final.
              Refunds are provided solely at Paevo&apos;s discretion (for example, in the event of a
              critical technical error on our platform that prevents report generation).
            </>,
            <>
              <LegalStrong>Enterprise Offerings:</LegalStrong> Enterprise services and ongoing
              monitoring may be subject to a separate Order Form, Statement of Work, or custom Master
              Services Agreement, which will govern in the event of a conflict with these Terms.
            </>,
          ]}
        />
      </LegalSection>

      <LegalSection title="8. Intellectual Property">
        <LegalList
          items={[
            <>
              <LegalStrong>Paevo IP:</LegalStrong> Paevo retains all right, title, and interest
              (including all intellectual property rights) in and to the Services, platform, underlying
              software, UI/UX, methodologies, algorithms, service framework, and generic templates.
            </>,
            <>
              <LegalStrong>Your Use of Outputs:</LegalStrong> Upon full payment of applicable fees,
              Paevo grants you a perpetual, non-exclusive, internal business license to use, download,
              and copy the paid Outputs generated specifically for your company. You may not resell,
              redistribute, or commercially publish the Outputs without Paevo&apos;s prior written
              consent.
            </>,
          ]}
        />
      </LegalSection>

      <LegalSection title="9. Beta and Evolving Services">
        <p>
          Paevo is an early-stage startup, and our platform is continually evolving. We may introduce
          new features, including beta or experimental features, which may contain bugs, undergo
          frequent changes, or be discontinued without notice. We are not liable for any downtime or
          loss of functionality as the platform evolves.
        </p>
      </LegalSection>

      <LegalSection title="10. Confidentiality">
        <p>
          Paevo agrees to treat your non-public Customer Data as confidential. We will not disclose
          your Customer Data to third parties except as necessary to provide the Services (e.g., to our
          secure sub-processors), as described in our Privacy Policy, or as required by law.
        </p>
      </LegalSection>

      <LegalSection title="11. Termination">
        <LegalList
          items={[
            <>
              <LegalStrong>By You:</LegalStrong> You may stop using the Services at any time. If you
              wish to close your account, you may do so through the platform or by contacting support.
            </>,
            <>
              <LegalStrong>By Paevo:</LegalStrong> We may suspend or terminate your access to the
              Services at any time, with or without cause, including for non-payment, breach of these
              Terms, or if we discontinue the Services.
            </>,
            <>
              <LegalStrong>Effect of Termination:</LegalStrong> Upon termination, your right to access
              the Services will immediately cease. Provisions regarding ownership, disclaimers,
              limitations of liability, arbitration, and indemnity shall survive termination.
            </>,
          ]}
        />
      </LegalSection>

      <LegalSection title="12. Warranties Disclaimer">
        <p className="uppercase">
          THE SERVICES AND OUTPUTS ARE PROVIDED ON AN &quot;AS IS&quot; AND &quot;AS AVAILABLE&quot;
          BASIS. TO THE MAXIMUM EXTENT PERMITTED BY LAW, PAEVO DISCLAIMS ALL WARRANTIES, EXPRESS OR
          IMPLIED, INCLUDING BUT NOT LIMITED TO IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
          PARTICULAR PURPOSE, ACCURACY, AND NON-INFRINGEMENT. WE DO NOT WARRANT THAT THE SERVICES WILL
          BE UNINTERRUPTED, ERROR-FREE, OR COMPLETELY SECURE.
        </p>
      </LegalSection>

      <LegalSection title="13. Limitation of Liability">
        <p className="uppercase">
          TO THE MAXIMUM EXTENT PERMITTED BY LAW, IN NO EVENT SHALL PAEVO, ITS DIRECTORS, EMPLOYEES,
          OR AFFILIATES BE LIABLE FOR ANY INDIRECT, PUNITIVE, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR
          EXEMPLARY DAMAGES, INCLUDING WITHOUT LIMITATION LOSS OF PROFITS, DATA, USE, GOODWILL, OR
          REVENUE, ARISING OUT OF OR IN CONNECTION WITH THE SERVICES OR THESE TERMS.
        </p>
        <p className="uppercase">
          IN NO EVENT SHALL PAEVO&apos;S TOTAL CUMULATIVE LIABILITY ARISING OUT OF OR RELATED TO THESE
          TERMS EXCEED THE GREATER OF (A) THE AMOUNT PAID BY YOU TO PAEVO IN THE TWELVE (12) MONTHS
          PRECEDING THE CLAIM, OR (B) ONE HUNDRED CANADIAN DOLLARS ($100 CAD).
        </p>
      </LegalSection>

      <LegalSection title="14. Indemnification">
        <p>
          You agree to indemnify, defend, and hold harmless Paevo and its officers, directors,
          employees, and agents from and against any claims, liabilities, damages, losses, and expenses
          (including reasonable legal fees) arising out of or in any way connected with: (a) your use of
          the Services; (b) your violation of these Terms; (c) your Customer Data, including any claims
          that your data infringes or violates third-party privacy or intellectual property rights; or
          (d) your reliance on any Outputs or business decisions made based on the Services.
        </p>
      </LegalSection>

      <LegalSection title="15. Governing Law">
        <p>
          These Terms shall be governed by and construed in accordance with the laws of the Province of
          Ontario and the federal laws of Canada applicable therein, without regard to conflict of law
          principles.
        </p>
      </LegalSection>

      <LegalSection title="16. Dispute Resolution, Binding Arbitration, and Class Action Waiver">
        <p>
          <LegalStrong>PLEASE READ THIS SECTION CAREFULLY AS IT AFFECTS YOUR LEGAL RIGHTS.</LegalStrong>
        </p>
        <LegalList
          items={[
            <>
              <LegalStrong>Binding Arbitration:</LegalStrong> Any dispute, controversy, or claim arising
              out of or relating to these Terms or the Services shall be settled by binding arbitration,
              rather than in court. The arbitration shall be conducted in Ontario, Canada, in accordance
              with the applicable commercial arbitration rules.
            </>,
            <>
              <LegalStrong>No Class Actions:</LegalStrong> You and Paevo agree that any dispute
              resolution proceedings will be conducted only on an individual basis and not in a class,
              consolidated, or representative action. You hereby waive any right to participate in any
              class action lawsuit or class-wide arbitration.
            </>,
            <>
              <LegalStrong>Exceptions:</LegalStrong> Notwithstanding the foregoing, either party may bring
              an individual action in small claims court or seek injunctive or other equitable relief in
              a court of competent jurisdiction located in Ontario, Canada to prevent the actual or
              threatened infringement, misappropriation, or violation of a party&apos;s intellectual
              property rights or data security.
            </>,
          ]}
        />
      </LegalSection>

      <LegalSection title="17. Changes to these Terms">
        <p>
          We reserve the right to modify these Terms at any time. If we make material changes, we will
          provide notice through the Services, via email, or by updating the &quot;Last Updated&quot;
          date at the top of these Terms. Your continued use of the Services following any such update
          constitutes your acceptance of the revised Terms.
        </p>
      </LegalSection>

      <LegalSection title="18. Contact Information">
        <p>If you have any questions about these Terms, please contact us at:</p>
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
