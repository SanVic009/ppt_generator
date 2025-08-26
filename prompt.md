**Primary goals (do all):**
* Replace Python `.pptx` generation with an HTML/CSS slide generator using **Tailwind CSS** (single-page slide deck or Reveal.js-style sections) that the backend can produce from the same slide content input (JSON/XML).
* Make the design agent behaviour explicit: *“Get as creative as you can in the design — especially the first slide.”*
* Avoid multiple slides that are just plain, single-color backgrounds with a centered bold heading. If more exist, automatically redesign extras into richer layouts.

---

**Deliverables (must produce):**

* Automatic transformation of repetitive plain slides into more engaging layouts.
* One example generated deck (10 slides) demonstrating variety and a unique first slide.
* A concise README or comment block explaining integration points (input format, output files, optional conversion to PPTX if requested).

---

**Design constraints and rules:**

**First slide (must be special & creative):**

* Use a hero layout: large headline, meaningful subtitle, distinctive visual (image/illustration/gradient/pattern), optional logo.
* Make it visually distinct from other slides (different layout, stronger visual hierarchy).
* Examples:

  * Full-bleed background image with overlay text (`bg-cover bg-center text-white flex items-center justify-center`).
  * Split-screen layout (`grid grid-cols-2 gap-8`).
  * Gradient background (`bg-gradient-to-r from-indigo-500 to-pink-500`).

**Creativity requirement:**

* *“Get as creative as you can”* — use Tailwind classes for varied layouts, e.g.:

  * Two-column: `grid grid-cols-2 gap-6`
  * Cards: `grid grid-cols-3 gap-4 p-8`
  * Timeline: flex-based vertical stacking with borders
  * Quotes: `italic border-l-4 pl-4`
* Keep a cohesive theme by defining Tailwind color palette and font families in `tailwind.config.js`.

---

**Implementation notes (practical):**

* Use semantic HTML5 `<section>` elements for slides, styled with Tailwind utilities:

  ```html
  <section class="slide min-h-screen flex flex-col items-center justify-center bg-gradient-to-r from-blue-500 to-purple-600 text-white">
    <h1 class="text-6xl font-bold mb-4">Title</h1>
    <p class="text-xl">Subtitle</p>
  </section>
  ```
* Use Tailwind’s `@apply` in a custom CSS file for reusable slide layouts.
* Keep JS minimal — just enough to map JSON content into HTML with Tailwind classes applied.
* If you use Reveal.js, still apply Tailwind classes for layout and design variety.
* Accessibility: ensure `text-white` on dark backgrounds meets contrast guidelines, add `alt` attributes to images.
* Assets: use `object-cover`, `rounded-xl`, `shadow-lg` for imagery.

---

**Integration & testing:**

* Include a function that scans all generated slides and enforces layout variety (no more than one plain slide).
* Provide at least one test that generates a sample input with multiple plain slides and verifies variety after transformation.
* Provide a preview command:

  ```bash
  npm run preview
  ```

  to serve `/dist/presentation.html`.

---


**Output format I expect from you (the AI editing the code):**

* A git-style patch or a small PR branch with:

  * `generator/html_generator.js` (or equivalent)
  * `/templates/slide_templates.html` with Tailwind classes
  * `/tailwind.config.js`
  * `/styles/tailwind.css` (compiled from Tailwind)
  * Example `/dist/presentation.html` (generated)
  * README notes for integration
* Clear commit messages and a brief changelog comment summarizing enforced rules.

---

**Non-goals / Do not do:**

* Do not modify the multi-agent system prompt or any system-level instructions.
* Do not generate multiple identical plain slides — redesign extras using Tailwind utility classes.

---

Do you want me to now **shorten this into a “one-shot” compact instruction** so another AI can process it without scrolling through this big block? That would make it easier to paste into your pipeline.



### Things I want to be done:
2025-08-15 20:11:08,989 - project_manager - INFO - Creating HTML presentation data with theme: Corporate Blue
2025-08-15 20:11:08,990 - project_manager - ERROR - Error generating presentation: 'RGBColor' object has no attribute 'rgb'
2025-08-15 20:11:08,990 - project_manager - ERROR - Error type: <class 'AttributeError'>
2025-08-15 20:11:08,991 - project_manager - INFO - [20250815_201012] failed: An error occurred during generation: 'RGBColor' object has no attribute 'rgb'
2025-08-15 20:11:08,991 - werkzeug - INFO - 127.0.0.1 - - [15/Aug/2025 20:11:08] "POST /api/presentations HTTP/1.1" 500 -
- Remove this error
- Currently there are no styles in the frontned. Make sure they are styled.
- Make sure the websocket updates are getting from the backend to frontend and being displayed in the correct position
- Currently the updates are being shown below the input box. make them appear besides the input box
- Show all the available themes below the main.

1. What is happening currently: The html code is static currently and the response from the previous agents is in natural language.  What I want you to do: Change the working of the code. Add another agent that takes the reponse of the designer agent an use that as the blueprint and convert it into html css code for each slide. In the preview section, add two round buttons that will have right and left arrow to navigate the slides generated
2. Store the reponse from the designer agent in a json file with the name as <project_title>_<timestamp>.json
3. Currently, all I can see is white background and black boxes. Connect the styles properly and make the style modern and something that is currently trending.
4. Connect the themes properly. There are themes in the code but I cant see them in the frontend. The available themes is empty curently

1. Use the html geneartor to actually generate a ppt based on the deisnger agent's prompt
2. Currently, It just generates the response.json and ends. I want a download ppt button that converts that created ppt into pdf and downloads it
3. Give updates after every agent is done giving response using websockets
3. Do not give the update of joined_room ....
4. "Error: JSON.parse: unexpected character at line 1 column 1 of the JSON data" I am getting this error. Resolve this

make another crew ai agent in agents.py file that uses the json response of the designer agent and designes a ppt following all the instructins from the json. Make use of reveal.js to display the ppt on the fornt end. Make the ppt in the aspect ration of 16:9.

use the agents2.py file as a template, add html_ppt_generator agent and change agents.py


This is a college in pune. Make the ppt for potential investors to invest in the college or university


I want to implement google custom search for content gathering in which it will take the response (which will be a json file response[slides][title]) from the planner agent, and put that title 