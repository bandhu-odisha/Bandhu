import { useState } from 'react'
import AnnualReportUploadModal from './AnnualReportUploadModal'

export default function Footer({ data }) {
  const urls = data?.urls || {}
  const contact = data?.contact || {}
  const annualReports = data?.annual_reports || []
  const isAdmin = Boolean(data?.user?.is_admin)
  const uploadAnnualReportUrl =
    data?.urls?.annual_reports_upload || '/annual-reports/upload/'
  const showAnnualSection = isAdmin || annualReports.length > 0
  const [uploadModalOpen, setUploadModalOpen] = useState(false)

  const initiatives = [
    { label: 'Ankurayan', href: urls.ankurayan || '#' },
    { label: 'Anandakendra', href: urls.anandakendra || '#' },
    { label: 'Bandhughar', href: urls.ashram || '#' },
    { label: 'Other Activities', href: urls.charity_work || '#' },
  ]

  return (
    <footer
      id="contact"
      data-cta-surface="dark"
      className="relative overflow-hidden border-t border-[#005E66] bg-[#005E66] px-4 py-14 text-white sm:px-6"
    >
      <div className="relative z-10 max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-10 lg:gap-12">
        <div>
          <h3 className="mb-2 font-heading text-xl font-bold text-white">Our Initiatives</h3>
          <div className="mb-6 h-1 w-14 rounded-full bg-white/70" />
          <ul className="space-y-2 font-body text-sm text-white/85">
            {initiatives.map((item) => (
              <li key={item.label}>
                <a
                  href={item.href}
                  className="text-white/90 transition hover:text-white underline-offset-2 hover:underline"
                >
                  {item.label}
                </a>
              </li>
            ))}
          </ul>

          {showAnnualSection && (
            <div className="mt-8">
              <h3 className="mb-2 font-heading text-xl font-bold text-white">Annual Reports</h3>
              <div className="mb-6 h-1 w-14 rounded-full bg-white/70" />
              <ul className="space-y-2 font-body text-sm text-white/85">
                {isAdmin && (
                  <li>
                    <button
                      type="button"
                      onClick={() => setUploadModalOpen(true)}
                      className="inline-flex items-center gap-2 text-white/90 transition hover:text-white underline-offset-2 hover:underline bg-transparent border-0 p-0 cursor-pointer font-inherit text-left"
                    >
                      <svg
                        className="h-4 w-4 shrink-0 opacity-90"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        aria-hidden
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                        />
                      </svg>
                      Upload annual report
                    </button>
                  </li>
                )}
                {annualReports.map((report) => (
                  <li key={report.id ?? report.year}>
                    <a
                      href={report.url}
                      className="inline-flex items-center gap-2 text-white/90 transition hover:text-white underline-offset-2 hover:underline"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <span>{report.title}</span>
                      <svg
                        className="h-3.5 w-3.5 shrink-0 opacity-80"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        aria-hidden
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                        />
                      </svg>
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div>
          <h3 className="mb-2 font-heading text-xl font-bold text-white">Contact Us</h3>
          <div className="mb-6 h-1 w-14 rounded-full bg-white/70" />
          <p className="mb-4 font-heading font-bold text-white">Bandhu</p>
          {contact.address && (
            <p className="mb-4 font-body text-sm leading-relaxed text-white/85">
              {contact.address}
            </p>
          )}
          <div className="space-y-3">
            {contact.contact_no && (
              <a
                href={`tel:${contact.contact_no.replace(/\s/g, '')}`}
                className="flex items-center gap-3 font-body text-sm text-white/85 transition hover:text-white"
              >
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-white/30 bg-white/15 text-white shadow-sm">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                </span>
                {contact.contact_no}
              </a>
            )}
            {contact.email && (
              <a
                href={`mailto:${contact.email}`}
                className="flex items-center gap-3 font-body text-sm text-white/85 transition hover:text-white"
              >
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-white/30 bg-white/15 text-white shadow-sm">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </span>
                {contact.email}
              </a>
            )}
          </div>
          <div className="flex gap-3 mt-6">
            {contact.facebook_link && (
              <a
                href={contact.facebook_link}
                target="_blank"
                rel="noopener noreferrer"
                className="flex h-10 w-10 items-center justify-center rounded-full border border-white/30 bg-white/15 text-white transition hover:bg-white/25 shadow-sm"
                aria-label="Facebook"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                </svg>
              </a>
            )}
            {contact.twitter_link && (
              <a
                href={contact.twitter_link}
                target="_blank"
                rel="noopener noreferrer"
                className="flex h-10 w-10 items-center justify-center rounded-full border border-white/30 bg-white/15 text-white transition hover:bg-white/25 shadow-sm"
                aria-label="Twitter"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
              </a>
            )}
          </div>
        </div>
      </div>

      {isAdmin && (
        <AnnualReportUploadModal
          open={uploadModalOpen}
          onClose={() => setUploadModalOpen(false)}
          uploadUrl={uploadAnnualReportUrl}
          csrfToken={data?.csrf_token}
        />
      )}
    </footer>
  )
}
