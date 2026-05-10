export default function Contact({ data }) {
  const contact = data?.contact
  if (!contact) return null

  return (
    <section id="contact" className="py-10 bg-white">
      <div className="max-w-4xl mx-auto px-4 sm:px-6">
        <h2 className="section-title text-center mb-3">
          Contact Us
        </h2>
        <div className="w-12 h-0.5 bg-teal mx-auto mb-12" />
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 sm:gap-6 text-center sm:text-left">
          <div className="flex flex-col items-center sm:items-start">
            <span className="flex items-center justify-center w-10 h-10 rounded-full bg-white text-teal-dark shadow-sm mb-3">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </span>
            <h3 className="font-heading font-semibold text-teal-dark mb-1 text-sm uppercase tracking-wide">Address</h3>
            <p className="font-body text-gray-600 text-sm leading-relaxed">{contact.address}</p>
          </div>
          <div className="flex flex-col items-center sm:items-start">
            <span className="flex items-center justify-center w-10 h-10 rounded-full bg-white text-teal-dark shadow-sm mb-3">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
            </span>
            <h3 className="font-heading font-semibold text-teal-dark mb-1 text-sm uppercase tracking-wide">Phone</h3>
            <a href={`tel:${contact.contact_no}`} className="font-body text-teal hover:underline text-sm">
              {contact.contact_no}
            </a>
          </div>
          <div className="flex flex-col items-center sm:items-start">
            <span className="flex items-center justify-center w-10 h-10 rounded-full bg-white text-teal-dark shadow-sm mb-3">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </span>
            <h3 className="font-heading font-semibold text-teal-dark mb-1 text-sm uppercase tracking-wide">Email</h3>
            <a href={`mailto:${contact.email}`} className="font-body text-teal hover:underline text-sm break-all">
              {contact.email}
            </a>
          </div>
        </div>
        <div className="flex justify-center gap-4 mt-10">
          {contact.facebook_link && (
            <a
              href={contact.facebook_link}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center w-10 h-10 rounded-full bg-white text-teal-dark shadow-sm hover:bg-teal hover:text-white transition"
              aria-label="Facebook"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
              </svg>
            </a>
          )}
          {contact.twitter_link && (
            <a
              href={contact.twitter_link}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center w-10 h-10 rounded-full bg-white text-teal-dark shadow-sm hover:bg-teal hover:text-white transition"
              aria-label="Twitter"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
            </a>
          )}
        </div>
      </div>
    </section>
  )
}
