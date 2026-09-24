## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4595 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.3976 | 0.88 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4541 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4559 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4596 | 1.00 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: grasp_place
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5136961687321454, -0.02302132862361297, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5540973523936195, 0.15165276355285293, 0.22199053588004086) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.459) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.25
  weight: 0.3
- id: place_goal
  target_entity: object
  weight: 0.5
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.08
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_grasp
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.01
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    grasp_z:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
- id: grasp_object
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_offset:
      type: scalar
      range:
      - -0.03
      - 0.0
      default: -0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.25
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.15
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: lift_object
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_adjust:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - generator.speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.01], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_offset: status=consumed; consumers=target.offset.z (replace)
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.25], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_adjust: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.459
- **task_score** (E): 1.000
- **fitness_score**: 0.979  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.1331 |
| descend_grasp | 1.00 | 0.1351 |
| grasp_object | 1.00 | 0.0117 |
| lift_object | 1.00 | 0.1149 |
| transport_to_goal | 1.00 | 0.2201 |
| descend_to_place | 1.00 | 0.0395 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.001, 0.171) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 |
| descend_grasp | descend | 1.00 / step_budget | (0.495, 0.001, 0.171)→(0.492, 0.001, 0.036) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.001, 0.036)→(0.484, 0.000, 0.028) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 |
| lift_object | lift | 1.00 / step_budget | (0.484, 0.000, 0.028)→(0.491, 0.000, 0.142) | (0.497, 0.000, 0.026)→(0.511, 0.000, 0.137) | 0.266→0.214 |
| transport_to_goal | approach | 1.00 / step_budget | (0.491, 0.000, 0.142)→(0.572, 0.166, 0.247) | (0.511, 0.000, 0.137)→(0.586, 0.166, 0.231) | 0.214→0.049 |
| descend_to_place | descend | 1.00 / step_budget | (0.572, 0.166, 0.247)→(0.577, 0.179, 0.210) | (0.586, 0.166, 0.231)→(0.589, 0.179, 0.191) | 0.049→0.011 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.690
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.399
- phase_breakdown.lift_object_score: 0.131
- phase_breakdown.place_goal_score: 0.643
- phase_breakdown.reach_grasp_score: 0.189
- grasp_place_fitness: 0.981

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.981
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.459
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.364


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57838,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10102,"approach_object.generator_speed":0.16957,"descend_grasp.grasp_z":0.00255,"descend_to_place.descend_speed":0.02482,"descend_to_place.place_z_adjust":0.02532,"grasp_object.grasp_offset":-0.00427,"lift_object.lift_height":0.12358,"transport_to_goal.transport_speed":0.06477},"optimized_scores":{"best_composite_score":0.45843,"best_fitness_score":0.97843,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.51156,-0.02214,-0.00149],"force_p95":0.5608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6056,"mean_force":0.17048,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49915,-0.0223,0.02906]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2917.0,"contact_point_centroid":[0.5039,-0.00317,0.07074],"force_p95":0.11006,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30443,"mean_force":0.07022,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50179,-0.02221,0.0681]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3249.0,"contact_point_centroid":[0.50389,-0.04113,0.0688],"force_p95":0.10477,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28936,"mean_force":0.06484,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50169,-0.02221,0.06704]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1026.0,"contact_point_centroid":[0.55381,0.15769,0.26643],"force_p95":0.13873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20258,"mean_force":0.09492,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54823,0.13925,0.26725]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1050.0,"contact_point_centroid":[0.55343,0.12111,0.26558],"force_p95":0.13316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20056,"mean_force":0.09052,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54828,0.13958,0.2663]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02281,-0.00206],"force_p95":0.14118,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19227,"mean_force":0.12773,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50143,-0.02236,0.02924]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5870.0,"contact_point_centroid":[0.53161,0.04009,0.20058],"force_p95":0.10883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18128,"mean_force":0.07957,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52675,0.05862,0.19941]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5428.0,"contact_point_centroid":[0.53222,0.07954,0.20318],"force_p95":0.11383,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1429,"mean_force":0.0837,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52738,0.06088,0.20174]},{"body_a":"world","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.5137,-0.02302,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50355,-0.00943,0.22619]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4089.0,"contact_point_centroid":[0.50089,-0.00313,0.03072],"force_p95":0.0779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12686,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50024,-0.02233,0.02797]},{"body_a":"world","body_b":"grasp_target","contact_count":1404.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50711,-0.021,0.09254]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.50091,-0.04143,0.02979],"force_p95":0.0699,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08811,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50024,-0.02233,0.02797]}],"total_contact_groups":12},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.56329,0.14482,0.23556],"final_tcp_position":[0.54937,0.14486,0.2527],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"phases":[{"n_steps":271.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.50847,-0.01957,0.1499],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12404,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":351.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.50852,-0.02251,0.03698],"tcp_start":[0.50847,-0.01957,0.1499],"tcp_to_object_dist_end":0.01213,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51357,-0.02224,0.02579],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26529,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.50021,-0.02233,0.02793],"tcp_start":[0.50852,-0.02251,0.03698],"tcp_to_object_dist_end":0.01353,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":190.0,"n_steps_budget":780.0,"object_pos_end":[0.52645,-0.02205,0.11562],"object_pos_start":[0.51357,-0.02224,0.02579],"object_to_goal_dist_end":0.20555,"object_to_goal_dist_start":0.26529,"object_z_max":0.11516,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.50739,-0.02215,0.12006],"tcp_start":[0.50021,-0.02233,0.02793],"tcp_to_object_dist_end":0.01957,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.56279,0.13466,0.2635],"object_pos_start":[0.52645,-0.02205,0.11562],"object_to_goal_dist_end":0.04569,"object_to_goal_dist_start":0.20555,"object_z_max":0.26318,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.54776,0.13484,0.27799],"tcp_start":[0.50739,-0.02215,0.12006],"tcp_to_object_dist_end":0.02088,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":99.0,"n_steps_budget":1000.0,"object_pos_end":[0.56329,0.14482,0.23556],"object_pos_start":[0.56279,0.13466,0.2635],"object_to_goal_dist_end":0.01776,"object_to_goal_dist_start":0.04569,"object_z_max":0.26385,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.54937,0.14486,0.2527],"tcp_start":[0.54776,0.13484,0.27799],"tcp_to_object_dist_end":0.02208,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40196,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.11792,"approach_object.generator_speed":0.17093,"descend_grasp.grasp_z":0.00171,"descend_to_place.descend_speed":0.0393,"descend_to_place.place_z_adjust":0.01575,"grasp_object.grasp_offset":-0.01424,"lift_object.lift_height":0.13224,"transport_to_goal.transport_speed":0.04846},"optimized_scores":{"best_composite_score":0.45919,"best_fitness_score":0.97919,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":67.0,"contact_point_centroid":[0.49925,0.04244,-0.0016],"force_p95":0.58735,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62241,"mean_force":0.18686,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48716,0.04306,0.02888]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3637.0,"contact_point_centroid":[0.49154,0.06183,0.07262],"force_p95":0.10518,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30916,"mean_force":0.06327,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48971,0.04285,0.07066]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3224.0,"contact_point_centroid":[0.4917,0.02379,0.07415],"force_p95":0.11135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29771,"mean_force":0.06864,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48977,0.04285,0.07144]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04464,-0.00217],"force_p95":0.17308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25881,"mean_force":0.13596,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48943,0.04329,0.02886]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1540.0,"contact_point_centroid":[0.56133,0.2113,0.18845],"force_p95":0.14954,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24627,"mean_force":0.09838,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55585,0.22982,0.18867]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1768.0,"contact_point_centroid":[0.56122,0.24823,0.18822],"force_p95":0.13538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22961,"mean_force":0.08964,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55583,0.22976,0.18888]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3718.0,"contact_point_centroid":[0.48943,0.02396,0.03072],"force_p95":0.08634,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15431,"mean_force":0.05625,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48827,0.04319,0.02764]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5346.0,"contact_point_centroid":[0.52944,0.11639,0.16933],"force_p95":0.11087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14677,"mean_force":0.07895,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52458,0.13497,0.16809]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5068.0,"contact_point_centroid":[0.53019,0.15556,0.17071],"force_p95":0.10967,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14509,"mean_force":0.08162,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52523,0.13685,0.16897]},{"body_a":"world","body_b":"grasp_target","contact_count":992.0,"contact_point_centroid":[0.50118,0.04505,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4985,0.01818,0.23411]},{"body_a":"world","body_b":"grasp_target","contact_count":1620.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49579,0.04076,0.1]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5253.0,"contact_point_centroid":[0.48843,0.0623,0.02997],"force_p95":0.07328,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08634,"mean_force":0.04299,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48827,0.04319,0.02764]}],"total_contact_groups":12},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.57159,0.23784,0.14867],"final_tcp_position":[0.55856,0.238,0.16647],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"phases":[{"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.49792,0.03782,0.16581],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14002,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":405.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.49637,0.04391,0.03625],"tcp_start":[0.49792,0.03782,0.16581],"tcp_to_object_dist_end":0.01136,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5011,0.04317,0.02544],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24375,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.48824,0.04318,0.02761],"tcp_start":[0.49637,0.04391,0.03625],"tcp_to_object_dist_end":0.01304,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":205.0,"n_steps_budget":840.0,"object_pos_end":[0.51433,0.04285,0.1239],"object_pos_start":[0.5011,0.04317,0.02544],"object_to_goal_dist_end":0.20939,"object_to_goal_dist_start":0.24375,"object_z_max":0.12343,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.49533,0.04281,0.12843],"tcp_start":[0.48824,0.04318,0.02761],"tcp_to_object_dist_end":0.01953,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.56995,0.22285,0.19536],"object_pos_start":[0.51433,0.04285,0.1239],"object_to_goal_dist_end":0.05362,"object_to_goal_dist_start":0.20939,"object_z_max":0.19518,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.55481,0.22309,0.20923],"tcp_start":[0.49533,0.04281,0.12843],"tcp_to_object_dist_end":0.02054,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":159.0,"n_steps_budget":1000.0,"object_pos_end":[0.57159,0.23784,0.14867],"object_pos_start":[0.56995,0.22285,0.19536],"object_to_goal_dist_end":0.01021,"object_to_goal_dist_start":0.05362,"object_z_max":0.19551,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.55856,0.238,0.16647],"tcp_start":[0.55481,0.22309,0.20923],"tcp_to_object_dist_end":0.02206,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34583,"average_solve_count":240.0,"average_success_count":240.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.14824,"approach_object.generator_speed":0.12335,"descend_grasp.grasp_z":0.00031,"descend_to_place.descend_speed":0.04778,"descend_to_place.place_z_adjust":0.01662,"grasp_object.grasp_offset":-0.0143,"lift_object.lift_height":0.18221,"transport_to_goal.transport_speed":0.02769},"optimized_scores":{"best_composite_score":0.4608,"best_fitness_score":0.9808,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.47382,-0.01949,-0.00147],"force_p95":0.61989,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63434,"mean_force":0.20419,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46302,-0.01952,0.0286]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1353.0,"contact_point_centroid":[0.62186,0.12913,0.22731],"force_p95":0.15175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31521,"mean_force":0.10582,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61818,0.14736,0.2316]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1472.0,"contact_point_centroid":[0.62101,0.1654,0.22737],"force_p95":0.15402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30023,"mean_force":0.10135,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61808,0.14725,0.23198]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4535.0,"contact_point_centroid":[0.46771,-0.00045,0.09452],"force_p95":0.11104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29094,"mean_force":0.06943,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46562,-0.01947,0.09202]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4939.0,"contact_point_centroid":[0.46769,-0.0384,0.09284],"force_p95":0.10735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28429,"mean_force":0.06499,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46555,-0.01947,0.09106]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5315.0,"contact_point_centroid":[0.54334,0.03811,0.21258],"force_p95":0.1282,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20418,"mean_force":0.08803,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53791,0.05652,0.2122]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4760.0,"contact_point_centroid":[0.54775,0.08013,0.21506],"force_p95":0.1325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19235,"mean_force":0.09475,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54243,0.0616,0.2146]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02001,-0.00205],"force_p95":0.13864,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18954,"mean_force":0.127,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4653,-0.01958,0.02857]},{"body_a":"world","body_b":"grasp_target","contact_count":780.0,"contact_point_centroid":[0.47616,-0.02015,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12325,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48932,-0.00759,0.25047]},{"body_a":"world","body_b":"grasp_target","contact_count":2048.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47389,-0.01783,0.11526]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4822.0,"contact_point_centroid":[0.46424,-0.00034,0.02989],"force_p95":0.06777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09521,"mean_force":0.04488,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46418,-0.01955,0.02748]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5162.0,"contact_point_centroid":[0.46409,-0.03878,0.02942],"force_p95":0.06657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08295,"mean_force":0.04298,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46419,-0.01955,0.02748]}],"total_contact_groups":12},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63331,0.15375,0.18771],"final_tcp_position":[0.62389,0.15383,0.21005],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":196.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_grasp","tcp_end":[0.47837,-0.01603,0.19768],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17173,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":512.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_grasp","tcp_end":[0.47201,-0.01972,0.03524],"tcp_start":[0.47837,-0.01603,0.19768],"tcp_to_object_dist_end":0.01012,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01958,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28822,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"reach_grasp","tcp_end":[0.46416,-0.01955,0.02745],"tcp_start":[0.47201,-0.01972,0.03524],"tcp_to_object_dist_end":0.01199,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.49237,-0.01947,0.17291],"object_pos_start":[0.47603,-0.01958,0.02581],"object_to_goal_dist_end":0.22705,"object_to_goal_dist_start":0.28822,"object_z_max":0.17244,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.47156,-0.01947,0.17851],"tcp_start":[0.46416,-0.01955,0.02745],"tcp_to_object_dist_end":0.02155,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":462.0,"n_steps_budget":1000.0,"object_pos_end":[0.62675,0.1414,0.23425],"object_pos_start":[0.49237,-0.01947,0.17291],"object_to_goal_dist_end":0.0479,"object_to_goal_dist_start":0.22705,"object_z_max":0.23411,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_goal","tcp_end":[0.61424,0.14153,0.2532],"tcp_start":[0.47156,-0.01947,0.17851],"tcp_to_object_dist_end":0.02271,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":152.0,"n_steps_budget":1000.0,"object_pos_end":[0.63331,0.15375,0.18771],"object_pos_start":[0.62675,0.1414,0.23425],"object_to_goal_dist_end":0.00621,"object_to_goal_dist_start":0.0479,"object_z_max":0.23431,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.62389,0.15383,0.21005],"tcp_start":[0.61424,0.14153,0.2532],"tcp_to_object_dist_end":0.02425,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```