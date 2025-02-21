document.addEventListener('load', () => {
  try {
    document.querySelector('.edit-this-page').remove()
    
    // remove these useless crap that appears on official readthedocs builds
    document.querySelector('#furo-readthedocs-versions').remove()
    document.querySelector('.injected').remove()
  } catch {
    // we're building this locally, forget it
  }
})

const tocDrawer = document.querySelector('aside.toc-drawer')

if (document.querySelector('section#topstats')) {
  // we don't need the right sidebar on the main landing page
  tocDrawer.remove()
} else {
  tocDrawer.style.visibility = 'visible'

  const enumProperties = [...document.querySelectorAll('em.property')].filter(x => x.children.length === 4)

  for (const enumProperty of enumProperties) {
    // we don't need to display enum values
    enumProperty.children[3].innerText = '...'
  }
}

// remove related pages in the footer
document.querySelector('.related-pages').remove()

// remove all header links
for (const headerLink of document.querySelectorAll('.headerlink')) {
  headerLink.remove()
}

for (const label of document.querySelectorAll('.sidebar-container label')) {
  const link = [...label.parentElement.children].find(child => child.nodeName === 'A')

  link.addEventListener('click', event => {
    event.preventDefault()
    label.click()
  })
}