<script lang="ts">
  import { browser } from "$app/environment";
  import { onMount } from "svelte";
  import * as THREE from "three";
  // import { CSS2DRenderer } from "three/examples/jsm/Addons.js";

  import { ArcballControls } from "three/examples/jsm/Addons.js";
  import { loadModel } from "$lib/utils/model_3d.js";
  import { baseUrl } from "$lib/constants.js";

  let { data } = $props();

  let prev: number = $derived(Number(data.offset) - Number(data.limit));
  let next: number = $derived(Number(data.offset) + Number(data.limit));

  let link: string = `${baseUrl}/protected/substructure/parallel/show-3d`;

  let currPage = $derived.by(() => {
    return Math.round(Number(data.offset) / Number(data.limit)) + 1;
  });
  let maxPage = $derived.by(() => {
    return Math.round(Number(data.totalSmile) / Number(data.limit)) + 1;
  });

  let linkPdbs = $derived.by(() => {
    return Number(data.offset) === 0
      ? `/substructure/parallel/${data.key}/pdbs`
      : `/substructure/parallel/${data.key}/pdbs-next-prev`;
  });

  //
  let pdbModels: (THREE.Object3D | null)[][] = $state([]); // 2D matrix
  let models: (THREE.Object3D | null)[] = $state([]);
  let hit = $state({ x: 0, y: 0, z: 0 });
  let modelSelected: THREE.Object3D | null = $state(null);
  // let modelSelectedOri: THREE.Object3D | null = $state(null);

  let plane1: THREE.Mesh<THREE.PlaneGeometry, THREE.MeshBasicMaterial>;
  let hover1: THREE.Mesh<THREE.PlaneGeometry, THREE.MeshBasicMaterial>;
  let raycaster = new THREE.Raycaster();
  let intersects: THREE.Intersection[] = $state([]);

  let isAnimate = $state(true);
  let isMoving = $state(false);
  // let isShowText = $state(true);

  let files: (string | null)[] = $state([]);
  let fileSelected: string | null = $state(null);
  let isHideH: boolean = $state(false); // Atom Hidrogen (toggle)
  // let isHidePolar: boolean = $state(false); // Hide Bound connect to H

  // Basic
  let container1: Element | HTMLElement;
  let container2: Element | HTMLElement;
  let scene1: THREE.Scene;
  let scene2: THREE.Scene;
  let camera1: THREE.PerspectiveCamera;
  let camera2: THREE.PerspectiveCamera;
  let renderer1: THREE.WebGLRenderer;
  let renderer2: THREE.WebGLRenderer;
  // let labelRenderer1: CSS2DRenderer;
  // let labelRenderer2: CSS2DRenderer;

  let dLight1: THREE.DirectionalLight;
  let dLight2a: THREE.DirectionalLight;
  let dLight2b: THREE.DirectionalLight;
  let controls1: ArcballControls;
  let controls2: ArcballControls;
  let mouse1: THREE.Vector2;
  // let mouse2: THREE.Vector2;
  let clock: THREE.Clock;

  // let isLoading = $state(false);

  function init() {
    container1 = document.getElementById("demo1")!;
    container2 = document.getElementById("demo2")!;
    // scene
    scene1 = new THREE.Scene();
    scene2 = new THREE.Scene();
    // camera
    const aspect1 = container1.clientWidth / container1.clientHeight;
    camera1 = new THREE.PerspectiveCamera(45, aspect1, 0.1, 1000);
    scene1.add(camera1);
    const aspect2 = container2.clientWidth / container2.clientHeight;
    camera2 = new THREE.PerspectiveCamera(45, aspect2, 0.1, 1000);
    scene2.add(camera2);
    // renderer
    // renderer1 = new THREE.WebGLRenderer({ antialias: true });
    renderer1 = new THREE.WebGLRenderer(); // without antialias for performance
    renderer1.setSize(container1.clientWidth, container1.clientHeight);
    //
    // renderer1.setPixelRatio(window.devicePixelRatio);
    // renderer2 = new THREE.WebGLRenderer({ antialias: true });
    renderer2 = new THREE.WebGLRenderer(); // without antialias for performance
    renderer2.setSize(container2.clientWidth, container2.clientHeight);
    // renderer2.setPixelRatio(window.devicePixelRatio);
    container1.appendChild(renderer1.domElement);
    container2.appendChild(renderer2.domElement);
    // label renderer
    // labelRenderer1 = new CSS2DRenderer();
    // labelRenderer1.setSize(container1.clientWidth, container1.clientHeight);
    // labelRenderer1.domElement.style.position = "absolute";
    // labelRenderer1.domElement.style.top = "0px";
    // labelRenderer1.domElement.style.pointerEvents = "none";
    // container1.appendChild(labelRenderer1.domElement);
    //
    // labelRenderer2 = new CSS2DRenderer();
    // labelRenderer2.setSize(container2.clientWidth, container2.clientHeight);
    // labelRenderer2.domElement.style.position = "absolute";
    // labelRenderer2.domElement.style.top = "0px";
    // labelRenderer2.domElement.style.pointerEvents = "none";
    // container2.appendChild(labelRenderer2.domElement);

    // directionalLight
    dLight1 = new THREE.DirectionalLight("white", 10);
    dLight1.position.set(-0.8, 1.8, 2.7);
    dLight1.target.position.set(0, 0, 0);
    // dLight1.castShadow = true;
    scene1.add(dLight1);
    scene1.add(new THREE.DirectionalLightHelper(dLight1, 0.2));
    //
    dLight2a = new THREE.DirectionalLight("white", 10);
    dLight2a.position.set(-0.4, 1, 1);
    dLight2a.target.position.set(0, 0, 0);
    // dLight2a.castShadow = true;
    scene2.add(dLight2a);
    scene2.add(new THREE.DirectionalLightHelper(dLight2a, 0.05));

    dLight2b = new THREE.DirectionalLight("white", 10);
    dLight2b.position.set(0.4, -1, -1);
    dLight2b.target.position.set(0, 0, 0);
    // dLight2b.castShadow = true;
    scene2.add(dLight2b);
    scene2.add(new THREE.DirectionalLightHelper(dLight2b, 0.05));

    // controls
    controls1 = new ArcballControls(camera1, renderer1.domElement, scene1);
    controls1.update();
    controls2 = new ArcballControls(camera2, renderer2.domElement, scene2);
    controls2.update();
    // helpers
    // scene1.add(new THREE.GridHelper(3, 6)); // size, division
    // scene2.add(new THREE.GridHelper(3, 6)); // size, division
    // scene1.add(new THREE.AxesHelper(2));
    // scene2.add(new THREE.AxesHelper(2));
    const axesHelper1 = new THREE.AxesHelper(2);
    axesHelper1.position.set(-3.5, 0, -3.5);
    scene1.add(axesHelper1);
    // const axesHelper2 = new THREE.AxesHelper(1);
    // axesHelper2.position.set(-0.7, 0, -0.7);
    // scene2.add(axesHelper2);
    //
    mouse1 = new THREE.Vector2();
    // mouse2 = new THREE.Vector2();
    clock = new THREE.Clock();
  }

  if (browser) {
    onMount(async () => {
      init();
      camera1.position.set(3, 4, 6);
      camera2.position.set(0.5, 1, 2);

      //* Your code here...
      //

      // -------------------------------------------
      // LEFT

      // Plane touched by raycaster, because real object/model cant be touched
      plane1 = new THREE.Mesh(
        new THREE.PlaneGeometry(4, 4),
        new THREE.MeshBasicMaterial({ side: THREE.DoubleSide, visible: false })
      );
      scene1.add(plane1);
      plane1.name = "ground";
      plane1.rotateX(Math.PI / 2);

      scene1.add(new THREE.GridHelper(4, 4));

      models = await loadModel(linkPdbs, data.files); // data.files already 16 items

      for (let i = 0; i < models.length; i++) {
        files.push(data.files[i]);
      }

      // IF the models.length < 16, then add [null] until total models = 16
      if (models.length < 16) {
        const totalEmptyBox = 16 - models.length;
        for (let i = 0; i < totalEmptyBox; i++) {
          models.push(null);
        }
      }

      let index = 0;
      for (let i = 0; i < 4; i++) {
        pdbModels[i] = [];
        for (let j = 0; j < 4; j++) {
          const model = models[index];
          if (model !== null) {
            model.scale.set(0.1, 0.1, 0.1);
          }
          pdbModels[i][j] = model;
          index += 1;
        }
      }
      models = [];

      // (4,4) Grid
      [-1.5, -0.5, 0.5, 1.5].forEach((x: number, i: number) => {
        [-1.5, -0.5, 0.5, 1.5].forEach((z: number, j: number) => {
          const model = pdbModels[i][j];
          if (model !== null) {
            pdbModels[i][j]!.position.set(x, 0.2, z);
            scene1.add(pdbModels[i][j]!);
          }
          models.push(pdbModels[i][j]);
        });
      });
      pdbModels = [];

      // Plate, unit(1,1) for blink
      hover1 = new THREE.Mesh(
        new THREE.PlaneGeometry(1, 1),
        new THREE.MeshBasicMaterial({
          side: THREE.DoubleSide,
          transparent: true,
          color: "darkslategray",
        })
      );
      scene1.add(hover1);
      hover1.rotateX(Math.PI / 2);
      hover1.position.set(0.5, 0, 0.5); // (4,4) Grid , geser 0.5 point

      // -------------------------------------------
      // RIGHT
      scene2.add(new THREE.GridHelper(1, 1));

      //
      let delta1 = 0;
      let interval1 = 1 / 10;
      // renderer1.setAnimationLoop(null);
      renderer1.setAnimationLoop((time: number) => {
        delta1 += clock.getDelta();
        if (delta1 > interval1) {
          tick1(time);
          renderer1.render(scene1, camera1);
          // labelRenderer1.render(scene1, camera1);
          controls1.update();
          delta1 = delta1 % interval1;
        }
      });
      renderer2.setAnimationLoop(() => {
        renderer2.render(scene2, camera2);
        // labelRenderer2.render(scene2, camera2);
        controls2.update();
      });

      function tick1(time: number) {
        if (isAnimate) {
          // everytime hovered plane, make it blink (transparent)
          // hover1.material.opacity = 1 + Math.sin(time / 120);
        }
        if (isMoving) {
          models.forEach((model) => {
            if (model !== null) {
              model.rotation.x = time / 1000;
              model.rotation.z = time / 1000;
              // bouncing y-axis
              model.position.y = 0.3 + 0.3 * Math.abs(Math.sin(time / 1000));
            }
          });
          // scene2.children.forEach((e) => {
          // e.position.set(0, 0, 0);
          // e.rotation.x = THREE.MathUtils.degToRad(10); // optional
          // e.rotation.x = time / 1000;
          // });
        }
      }

      //
    });
  }
</script>

<svelte:window
  onresize={() => {
    camera1.aspect = container1.clientWidth / container1.clientHeight;
    camera1.updateProjectionMatrix();
    renderer1.setSize(container1.clientWidth, container1.clientHeight);
    // labelRenderer1.setSize(container1.clientWidth, container1.clientHeight);

    camera2.aspect = container2.clientWidth / container2.clientHeight;
    camera2.updateProjectionMatrix();
    renderer2.setSize(container2.clientWidth, container2.clientHeight);
    // labelRenderer2.setSize(container2.clientWidth, container2.clientHeight);
  }}
  onmousemove={(e: MouseEvent) => {
    const rect1 = renderer1.domElement.getBoundingClientRect();
    mouse1.x = ((e.clientX - rect1.left) / container1.clientWidth) * 2 - 1;
    mouse1.y = -((e.clientY - rect1.top) / container1.clientHeight) * 2 + 1;

    // const rect2 = renderer2.domElement.getBoundingClientRect();
    // mouse2.x = ((e.clientX - rect2.left) / container2.clientWidth) * 2 - 1;
    // mouse2.y = -((e.clientY - rect2.top) / container2.clientHeight) * 2 + 1;

    renderer1.domElement.style.cursor = "auto";

    // Raycaster only for LEFT
    raycaster.setFromCamera(mouse1, camera1);
    intersects = raycaster.intersectObjects(scene1.children, false);
    intersects.forEach((intersect) => {
      if (intersect.object.name === "ground") {
        // (4,4) Grid (Genap),
        // intersect.point will be auto-normalized by Vector3()
        const currPoss = new THREE.Vector3()
          .copy(intersect.point)
          .floor()
          .addScalar(0.5); // addScalar geser 0.5
        // console.log(`${currPos.x}, ${currPos.z}`);
        renderer1.domElement.style.cursor = "pointer";
        hover1.position.set(currPoss.x, 0, currPoss.z);

        models.forEach(async (model, i) => {
          if (model !== null) {
            if (
              model.position.x === currPoss.x &&
              model.position.z === currPoss.z
            ) {
              hit.x = currPoss.x;
              hit.y = currPoss.y;
              hit.z = currPoss.z;

              fileSelected = files[i];

              // if (isShowText) {
              //   model = await loadSingleWithText(
              //     fileSelected!,
              //     document,
              //     container2
              //   );
              //   model.scale.set(0.1, 0.1, 0.1);
              // }

              modelSelected = model.clone();
              if (isHideH) {
                modelSelected.children.forEach((child, i) => {
                  if (child.name === "H" || child.name === "H-bound") {
                    (child as THREE.Mesh).visible = false;
                    // group.remove(child);
                  }
                });
              }

              // modelSelectedOri = model.clone();

              // // HidePolar is Hide H also its bound
              // if (isHidePolar) {
              //   const group = model.clone();
              //   group.children.forEach((child, i) => {
              //     if (child.name === "H" || child.name === "polar") {
              //       (child as THREE.Mesh).visible = false;
              //       // group.remove(child);
              //     }
              //   });
              //   isHideH = true; // make it H hide also
              //   modelSelected = group;
              // } else {
              //   if (isHideH) {
              //     const group = model.clone();
              //     group.children.forEach((child, i) => {
              //       if (child.name === "H") {
              //         // const mesh = child as THREE.Mesh;
              //         // mesh.material = (child as THREE.Mesh).material as THREE.MeshPhongMaterial;
              //         // (mesh.material as THREE.MeshPhongMaterial).color.set(0x00000);
              //         // mesh.visible = false;
              //         (child as THREE.Mesh).visible = false;
              //         // group.remove(child);
              //       }
              //     });
              //     isHidePolar = false;
              //     modelSelected = group;
              //   } else {
              //     isHidePolar = false;
              //     isHideH = false;
              //     modelSelected = model.clone();
              //   }
              // }

              modelSelected.name = "modelSelected";

              // Delete existing model in screen2 if exist
              scene2.children.forEach((e) => {
                if (e.name === "modelSelected") {
                  scene2.remove(e);
                }
              });
              scene2.add(modelSelected); // add a new model to scene2
              modelSelected.position.set(0, 0, 0);
              // modelSelected.rotation.x = THREE.MathUtils.degToRad(i * 10); // optional
            }
          }
        });
      }
    });
  }}
/>

<div class="grid grid-cols-2 gap-0.5 h-screen w-full">
  <div id="demo1" class="flex place-content-center m-0 overflow-hidden">
    <!-- Stop/Start Bouncing Button -->
    <button
      class="absolute w-full/2 left-5 top-2 btn btn-md bg-white text-black"
      onclick={() => {
        isMoving = !isMoving;
      }}>{isMoving ? "Stop" : "Start"} Bouncing</button
    >
    <!-- Reset Button -->
    <button
      class="absolute w-full/2 left-41 top-2 btn btn-md bg-white text-black"
      onclick={() => {
        controls1.reset();
        camera1.position.set(3, 4, 6);
      }}>Reset</button
    >
    <!-- Next / Prev -->
    <a
      target="_self"
      href={`${link}?key=${data.key}&name=${data.name}&offset=${prev}&limit=${data.limit}`}
      aria-disabled={`${Number(data.offset) === 0 ? "true" : "false"}`}
      class={`absolute w-full/2 left-64 top-2 btn btn-md bg-white  text-black ${Number(data.offset) === 0 ? "btn-disabled" : ""}`}
      >👈Prev</a
    >
    {#if currPage}
      <span
        class="absolute w-full/2 left-86 top-2 bg-white text-md border border-slate-400 rounded-full p-2"
        >{currPage}/{maxPage}</span
      >
    {:else}
      <span
        class="absolute w-full/2 left-86 top-2 bg-white text-md border border-slate-400 rounded-full p-2"
        >. / .</span
      >
    {/if}
    <a
      target="_self"
      href={`${link}?key=${data.key}&name=${data.name}&offset=${next}&limit=${data.limit}`}
      aria-disabled={`${currPage === maxPage ? "true" : "false"}`}
      class={`absolute w-full/2 left-98 top-2 btn btn-md bg-white text-black ${currPage === maxPage ? "btn-disabled" : ""}`}
      >Next👉</a
    >
    <!-- Collision Button -->
    <a
      target="_blank"
      href={`${baseUrl}/protected/substructure/parallel/collision?key=${data.key}&name=${data.name}&offset=${data.offset}&limit=${data.limit}`}
      class="absolute w-full/2 right-[calc(50%+8.2em)] top-2 btn btn-lg bg-white text-black"
      >Collision</a
    >
    <!-- Reaction Button -->
    <a
      target="_blank"
      href={`${baseUrl}/protected/substructure/parallel/reaction?key=${data.key}&name=${data.name}&offset=${data.offset}&limit=${data.limit}`}
      class="absolute w-full/2 right-[calc(50%+1.2em)] top-2 btn btn-lg bg-white text-black"
      >Reaction</a
    >
    <!-- file's list, left scene -->
    <div
      class="absolute w-32 left-8 top-[calc(12%)] text-sm text-white border-t-2 border-b-2 border-b-red-400 pt-2 pb-2 flex flex-wrap"
    >
      {#each files as file, index}
        <p
          class={`shrink-0 ${fileSelected === file ? "text-red-400 font-semibold" : "text-white"}`}
        >
          {index + 1}. {file}
        </p>
      {/each}
    </div>
  </div>

  <div id="demo2" class="flex place-content-center m-0 overflow-hidden">
    <!-- Reset Button -->
    <button
      class="absolute w-full/2 top-2 btn btn-lg bg-white text-black"
      onclick={() => {
        controls2.reset();
        camera2.position.set(0.5, 1, 2);
      }}>Reset</button
    >
    <!-- Details Button -->
    <!--
    <form method="POST" action="?/details" use:enhance={details}>
      <input type="hidden" name="name" hidden value={fileSelected} />
      {#if isLoading}
        <button
          class="absolute w-full/2 right-5 top-2 btn btn-lg bg-white text-black btn-disabled"
        >
          <span class="loading loading-spinner"></span>
          loading
        </button>
      {:else}
        <button
          class="absolute w-full/2 left-[calc(50%+1.2em)] top-2 btn btn-lg bg-white text-black"
          >3DMol</button
        >
      {/if}
    </form>
    -->
    <!-- Cubemap Button -->
    <!-- <form method="POST" action="?/cubemap" use:enhance={cubemap}>
      <input type="hidden" name="name" hidden value={data.name} />
      <input type="hidden" name="fileSelected" hidden value={fileSelected} />
      <button
        class="absolute w-full/2 right-[1.2em] top-2 btn btn-lg bg-white text-black"
        >Realistic</button
      >
    </form> -->
    <!-- <a
      target="_blank"
      href={`${baseUrl}/protected/substructure/parallel/collision?key=${data.key}&name=${data.name}&offset=0&limit=16`}
      class="absolute w-full/2 left-[calc(50%+1.2em)] top-2 btn btn-lg bg-white text-black"
      >Collision</a
    > -->
    <a
      target="_blank"
      href={`${baseUrl}/protected/substructure/parallel/cubemap?subDir=${data.key}&file=${fileSelected}`}
      class="absolute w-full/2 right-[1.2em] top-2 btn btn-lg bg-white text-black"
      >Realistic</a
    >
    <!-- name -->
    <div class="absolute top-[calc(9%)] text-lg text-white">
      {fileSelected}
    </div>
    <!-- Text (molecule's symbols), right scene -->
    <div
      class="absolute w-48 left-[calc(50%+2rem)] top-[calc(12%)] text-sm text-white rounded-r-box border-r-2 border-b-2 border-b-red-400 pr-1 pb-2"
    >
      <div class="flex items-center space-x-1">
        <span class="font-semibold">H</span>
        <span>white</span>
        <span class="font-semibold ml-2">
          <div class="flex flex-col space-y-2">
            <button
              class="btn btn-xs bg-white text-black"
              onclick={() => {
                isHideH = !isHideH;
                if (!modelSelected) return;
                modelSelected.children.forEach((child, i) => {
                  if (child.name === "H" || child.name === "H-bound") {
                    (child as THREE.Mesh).visible = isHideH ? false : true;
                    // modelSelected.remove(child);
                  }
                });
                // Delete existing model in screen2 if exist
                scene2.children.forEach((e) => {
                  if (e.name === "modelSelected") {
                    scene2.remove(e);
                  }
                });
                scene2.add(modelSelected); // add a new model to scene2
                modelSelected.position.set(0, 0, 0);
                // modelSelected.rotation.x = THREE.MathUtils.degToRad(i * 10); // optional
              }}
            >
              {isHideH ? "Show Hydrogen" : "Hide Hydrogen"}
            </button>
          </div>
        </span>
      </div>
      <p><span class="text-gray-500 font-semibold">C</span> grey</p>
      <p><span class="font-semibold text-blue-500">N</span> blue</p>
      <p><span class="font-semibold text-red-500">O</span> red</p>
      <p><span class="font-semibold text-purple-500">P</span> purple</p>
      <p><span class="font-semibold text-yellow-300">S</span> yellow</p>
      <p><span class="font-semibold text-green-500">F</span> green</p>
      <p><span class="font-semibold text-lime-500">Cl</span> limegreen</p>
      <p><span class="font-semibold text-pink-500">Br</span> pink</p>
      <p><span class="font-semibold text-[#e400f5]">I</span> magentas</p>
      <p><span class="font-semibold text-orange-500">Si</span> orange</p>
    </div>
  </div>
</div>
