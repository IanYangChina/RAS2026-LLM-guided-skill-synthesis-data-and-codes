## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.3350 | 1.00 | ✅ accepted |
| 10 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.1398 | 0.70 | ❌ rejected |
| 9 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | -0.2118 | 0.18 | ❌ rejected |
| 8 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | 0.2263 | 0.87 | ❌ rejected |
| 7 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | 0.2857 | 0.90 | ❌ rejected |

**Proposal policy**: task_score is 0.90 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

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
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
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
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

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
| `object` | offset from object initial position (0.5125095466604667, 0.039721380096957554, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | final destination targets |
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

## Current Skill (Q=0.286) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: reach_grasp_height
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.2
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_above
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.1
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.3
phases:
- id: descend_approach
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_approach
- id: descend_to_grasp
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
    - 0.03
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_height:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp_height
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
    tolerance: 0.005
  guards:
  - id: grasp_closed
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: reach_grasp_height
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
    - 0.15
    tolerance: 0.025
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_clearance
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.07
    orientation:
      mode: keep_current
  parameters:
    transport_height:
      type: scalar
      range:
      - 0.06
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_above
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    place_height_offset:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.015
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_approach** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_height: status=consumed; consumers=target.offset.z (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - parameter_bindings: none
  - guards:
    - id=grasp_closed, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.01
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.025
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.1], tolerance=0.07
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.03], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_height_offset: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.286
- **task_score** (E): 0.899
- **fitness_score**: 0.906  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_approach | 1.00 | 1.00 | 0.1572 |
| descend_to_grasp | 1.00 | 1.00 | 0.0885 |
| grasp_object | 1.00 | 1.00 | 0.0123 |
| lift_object | 1.00 | 1.00 | 0.1086 |
| transport_to_goal | 0.00 | 1.00 | 0.2010 |
| descend_to_place | 1.00 | 1.00 | 0.0484 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_approach | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.019, 0.148) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.019, 0.148)→(0.505, 0.022, 0.060) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.505, 0.022, 0.060)→(0.497, 0.021, 0.051) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.025) | 0.273→0.274 | 1.00 / 36.000 | 0.168 | 0.214 |
| lift_object | lift | 1.00 / step_budget | (0.497, 0.021, 0.051)→(0.505, 0.021, 0.159) | (0.511, 0.022, 0.025)→(0.513, 0.022, 0.131) | 0.274→0.224 | 1.00 / 26.333 | 0.119 | 0.315 |
| transport_to_goal | approach | 0.00 / step_budget | (0.505, 0.021, 0.159)→(0.583, 0.164, 0.271) | (0.513, 0.022, 0.131)→(0.590, 0.163, 0.241) | 0.224→0.070 | 1.00 / 28.667 | 55983.992 | 0.196 |
| descend_to_place | descend | 1.00 / step_budget | (0.583, 0.164, 0.271)→(0.595, 0.191, 0.234) | (0.590, 0.163, 0.241)→(0.604, 0.191, 0.203) | 0.070→0.023 | 1.00 / 19.333 | 0.132 | 0.464 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.005
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.558
- phase_breakdown.reach_grasp_height_score: 0.719
- phase_breakdown.lift_clearance_score: 0.506
- phase_breakdown.reach_goal_score: 0.603
- phase_breakdown.transport_above_score: 0.235
- phase_breakdown.reach_approach_score: 0.541
- grasp_place_fitness: 0.957

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.957
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.265
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend_to_grasp.grasp_height
- **Final σ (mean)**: 0.381


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.6716,"average_solve_count":405.0,"average_success_count":405.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.11159,"descend_approach.approach_speed":0.02241,"descend_to_grasp.descend_speed":0.04916,"descend_to_grasp.grasp_height":0.02,"descend_to_place.place_height_offset":0.03043,"descend_to_place.place_speed":0.00566,"lift_object.lift_height":0.14523,"lift_object.lift_speed":0.04285,"transport_to_goal.transport_height":0.0948,"transport_to_goal.transport_speed":0.07071},"optimized_scores":{"best_composite_score":0.33675,"best_fitness_score":0.95675,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1415.0,"contact_point_centroid":[0.60053,0.1556,0.19316],"force_p95":0.14834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50959,"mean_force":0.09186,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59684,0.1372,0.1945]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1125.0,"contact_point_centroid":[0.60085,0.11964,0.19109],"force_p95":0.15055,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42792,"mean_force":0.10674,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59754,0.13805,0.19369]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.50932,0.03709,-0.00174],"force_p95":0.31537,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35025,"mean_force":0.133,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49834,0.0376,0.05156]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3493.0,"contact_point_centroid":[0.50168,0.01846,0.08956],"force_p95":0.12238,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31427,"mean_force":0.08247,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50095,0.03758,0.09118]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5506.0,"contact_point_centroid":[0.50099,0.05614,0.0954],"force_p95":0.092,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25912,"mean_force":0.05581,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50137,0.03759,0.09531]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.03963,-0.00218],"force_p95":0.17613,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22299,"mean_force":0.13583,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50035,0.03778,0.05175]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1865.0,"contact_point_centroid":[0.54274,0.09361,0.16911],"force_p95":0.12972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21209,"mean_force":0.07149,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54216,0.07519,0.16935]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1502.0,"contact_point_centroid":[0.5465,0.06079,0.17067],"force_p95":0.14456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18778,"mean_force":0.08426,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54632,0.07966,0.1721]},{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.51251,0.03972,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.50267,0.01584,0.23204]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3552.0,"contact_point_centroid":[0.50141,0.01857,0.05018],"force_p95":0.10846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13179,"mean_force":0.06122,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49921,0.03769,0.05048]},{"body_a":"world","body_b":"grasp_target","contact_count":1000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50615,0.0358,0.10981]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4862.0,"contact_point_centroid":[0.49998,0.05649,0.0508],"force_p95":0.07503,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07856,"mean_force":0.04393,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49922,0.03769,0.05049]}],"total_contact_groups":12},"final_pose_error":0.02525,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.6194,0.15466,0.14821],"final_tcp_position":[0.6105,0.15426,0.17902],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.50959,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1208.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.50731,0.03352,0.15964],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":250.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.50733,0.03832,0.05975],"tcp_start":[0.50731,0.03352,0.15964],"tcp_to_object_dist_end":0.03416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51247,0.03816,0.02525],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21365,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.17654,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10214.0,"raw_peak_contact_force":0.22299,"subtask_id":"reach_grasp_height","tcp_end":[0.49918,0.03768,0.05045],"tcp_start":[0.50733,0.03832,0.05975],"tcp_to_object_dist_end":0.02849,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":263.0,"n_steps_budget":1000.0,"object_pos_end":[0.51543,0.03878,0.11868],"object_pos_start":[0.51247,0.03816,0.02525],"object_to_goal_dist_end":0.17651,"object_to_goal_dist_start":0.21365,"object_z_max":0.11833,"peak_contact_force":0.11861,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9085.0,"raw_peak_contact_force":0.35025,"subtask_id":"lift_clearance","tcp_end":[0.5069,0.03778,0.14649],"tcp_start":[0.49918,0.03768,0.05045],"tcp_to_object_dist_end":0.0291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":116.0,"n_steps_budget":1000.0,"object_pos_end":[0.59781,0.12742,0.17312],"object_pos_start":[0.51543,0.03878,0.11868],"object_to_goal_dist_end":0.0609,"object_to_goal_dist_start":0.17651,"object_z_max":0.17255,"peak_contact_force":0.1108,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3367.0,"raw_peak_contact_force":0.21209,"subtask_id":"transport_above","tcp_end":[0.59022,0.12744,0.20258],"tcp_start":[0.5069,0.03778,0.14649],"tcp_to_object_dist_end":0.03042,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.6194,0.15466,0.14821],"object_pos_start":[0.59781,0.12742,0.17312],"object_to_goal_dist_end":0.0199,"object_to_goal_dist_start":0.0609,"object_z_max":0.17519,"peak_contact_force":0.13095,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2540.0,"raw_peak_contact_force":0.50959,"subtask_id":"reach_goal","tcp_end":[0.6105,0.15426,0.17902],"tcp_start":[0.59022,0.12744,0.20258],"tcp_to_object_dist_end":0.03208,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.81667,"average_solve_count":420.0,"average_success_count":420.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.11478,"descend_approach.approach_speed":0.08933,"descend_to_grasp.descend_speed":0.02341,"descend_to_grasp.grasp_height":0.02015,"descend_to_place.place_height_offset":0.0361,"descend_to_place.place_speed":0.00915,"lift_object.lift_height":0.16145,"lift_object.lift_speed":0.03422,"transport_to_goal.transport_height":0.14911,"transport_to_goal.transport_speed":0.07732},"optimized_scores":{"best_composite_score":0.25581,"best_fitness_score":0.87581,"best_task_score":0.84051},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1090.0,"contact_point_centroid":[0.57057,0.21803,0.30719],"force_p95":0.18177,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43023,"mean_force":0.10956,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56682,0.19953,0.31022]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.47964,0.04662,-0.00172],"force_p95":0.28854,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30782,"mean_force":0.1312,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46988,0.04624,0.05306]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3380.0,"contact_point_centroid":[0.47196,0.0275,0.10099],"force_p95":0.12255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2871,"mean_force":0.08808,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47256,0.04629,0.10328]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4294.0,"contact_point_centroid":[0.47275,0.06478,0.09846],"force_p95":0.1131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27182,"mean_force":0.07409,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47229,0.04628,0.10012]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2307.0,"contact_point_centroid":[0.51878,0.09759,0.2385],"force_p95":0.12448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22928,"mean_force":0.08559,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51929,0.11627,0.24096]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04854,-0.00219],"force_p95":0.177,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2273,"mean_force":0.13662,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47188,0.04644,0.05325]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2635.0,"contact_point_centroid":[0.5164,0.13084,0.23452],"force_p95":0.11689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21716,"mean_force":0.07548,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51693,0.11229,0.2364]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1082.0,"contact_point_centroid":[0.56985,0.18079,0.30849],"force_p95":0.13398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20506,"mean_force":0.1033,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56654,0.19891,0.31162]},{"body_a":"world","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.49101,0.01968,0.23294]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2419.0,"contact_point_centroid":[0.47176,0.02746,0.04976],"force_p95":0.10798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13607,"mean_force":0.08291,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4708,0.04634,0.05213]},{"body_a":"world","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47934,0.04388,0.11258]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4194.0,"contact_point_centroid":[0.47153,0.06509,0.05118],"force_p95":0.09079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09552,"mean_force":0.05275,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47081,0.04634,0.05214]}],"total_contact_groups":12},"final_pose_error":0.02445,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58127,0.21287,0.25106],"final_tcp_position":[0.57309,0.21314,0.28313],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1096.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.48245,0.04107,0.16311],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13731,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1088.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.47854,0.04706,0.06042],"tcp_start":[0.48245,0.04107,0.16311],"tcp_to_object_dist_end":0.03469,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48267,0.04704,0.02526],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29157,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.17032,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8413.0,"raw_peak_contact_force":0.2273,"subtask_id":"reach_grasp_height","tcp_end":[0.47077,0.04634,0.0521],"tcp_start":[0.47854,0.04706,0.06042],"tcp_to_object_dist_end":0.02936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.48335,0.04713,0.13291],"object_pos_start":[0.48267,0.04704,0.02526],"object_to_goal_dist_end":0.22859,"object_to_goal_dist_start":0.29157,"object_z_max":0.13254,"peak_contact_force":0.11673,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7764.0,"raw_peak_contact_force":0.30782,"subtask_id":"lift_clearance","tcp_end":[0.47774,0.04659,0.16257],"tcp_start":[0.47077,0.04634,0.0521],"tcp_to_object_dist_end":0.03019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":192.0,"n_steps_budget":1000.0,"object_pos_end":[0.56958,0.19025,0.29526],"object_pos_start":[0.48335,0.04713,0.13291],"object_to_goal_dist_end":0.0764,"object_to_goal_dist_start":0.22859,"object_z_max":0.29433,"peak_contact_force":167951.73011,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4942.0,"raw_peak_contact_force":0.22928,"subtask_id":"transport_above","tcp_end":[0.56287,0.1902,0.32601],"tcp_start":[0.47774,0.04659,0.16257],"tcp_to_object_dist_end":0.03147,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.58127,0.21287,0.25106],"object_pos_start":[0.56958,0.19025,0.29526],"object_to_goal_dist_end":0.02606,"object_to_goal_dist_start":0.0764,"object_z_max":0.29835,"peak_contact_force":0.13082,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.43023,"subtask_id":"reach_goal","tcp_end":[0.57309,0.21314,0.28313],"tcp_start":[0.56287,0.1902,0.32601],"tcp_to_object_dist_end":0.0331,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.46629,"average_solve_count":534.0,"average_success_count":534.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.07501,"descend_approach.approach_speed":0.05194,"descend_to_grasp.descend_speed":0.01636,"descend_to_grasp.grasp_height":0.02068,"descend_to_place.place_height_offset":0.01632,"descend_to_place.place_speed":0.00792,"lift_object.lift_height":0.16705,"lift_object.lift_speed":0.01947,"transport_to_goal.transport_height":0.11691,"transport_to_goal.transport_speed":0.02926},"optimized_scores":{"best_composite_score":0.26467,"best_fitness_score":0.88467,"best_task_score":0.85636},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1235.0,"contact_point_centroid":[0.60185,0.20647,0.26328],"force_p95":0.16289,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.453,"mean_force":0.09945,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5981,0.18769,0.26555]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1588.0,"contact_point_centroid":[0.59996,0.16871,0.2659],"force_p95":0.12309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3095,"mean_force":0.07926,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59787,0.1867,0.26731]},{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.53455,-0.0203,-0.0017],"force_p95":0.2627,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28658,"mean_force":0.12967,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52111,-0.02039,0.05079]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5276.0,"contact_point_centroid":[0.52541,-0.00136,0.09987],"force_p95":0.11889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23377,"mean_force":0.06935,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52439,-0.02044,0.09994]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6774.0,"contact_point_centroid":[0.52541,-0.03905,0.1053],"force_p95":0.09,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21423,"mean_force":0.05536,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52489,-0.02045,0.1049]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53709,-0.02131,-0.0021],"force_p95":0.15396,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19065,"mean_force":0.12991,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52338,-0.02044,0.05152]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2246.0,"contact_point_centroid":[0.56234,0.08866,0.21795],"force_p95":0.12639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14708,"mean_force":0.08645,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5612,0.06992,0.22024]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3697.0,"contact_point_centroid":[0.55927,0.04588,0.21699],"force_p95":0.10395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14129,"mean_force":0.05911,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55932,0.06431,0.21693]},{"body_a":"world","body_b":"grasp_target","contact_count":1472.0,"contact_point_centroid":[0.53702,-0.02132,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.51317,-0.009,0.2127]},{"body_a":"world","body_b":"grasp_target","contact_count":680.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52838,-0.01952,0.09265]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4348.0,"contact_point_centroid":[0.52329,-0.00121,0.05048],"force_p95":0.08582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11849,"mean_force":0.05268,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52219,-0.02041,0.05013]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4926.0,"contact_point_centroid":[0.52318,-0.03941,0.05051],"force_p95":0.06998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07241,"mean_force":0.04363,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5222,-0.02041,0.05014]}],"total_contact_groups":12},"final_pose_error":0.02777,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61129,0.20456,0.20895],"final_tcp_position":[0.60281,0.20616,0.2395],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.453,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1472.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.52886,-0.01866,0.12264],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":170.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":680.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp_height","tcp_end":[0.53057,-0.02055,0.0602],"tcp_start":[0.52886,-0.01866,0.12264],"tcp_to_object_dist_end":0.03479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53703,-0.02069,0.02557],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31648,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.15573,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11074.0,"raw_peak_contact_force":0.19065,"subtask_id":"reach_grasp_height","tcp_end":[0.52216,-0.02041,0.0501],"tcp_start":[0.53057,-0.02055,0.0602],"tcp_to_object_dist_end":0.02868,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.53992,-0.02139,0.14019],"object_pos_start":[0.53703,-0.02069,0.02557],"object_to_goal_dist_end":0.26748,"object_to_goal_dist_start":0.31648,"object_z_max":0.13985,"peak_contact_force":0.1205,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12160.0,"raw_peak_contact_force":0.28658,"subtask_id":"lift_clearance","tcp_end":[0.53162,-0.02058,0.16837],"tcp_start":[0.52216,-0.02041,0.0501],"tcp_to_object_dist_end":0.02939,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":201.0,"n_steps_budget":1000.0,"object_pos_end":[0.60272,0.17216,0.25346],"object_pos_start":[0.53992,-0.02139,0.14019],"object_to_goal_dist_end":0.07258,"object_to_goal_dist_start":0.26748,"object_z_max":0.2528,"peak_contact_force":0.13483,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5943.0,"raw_peak_contact_force":0.14708,"subtask_id":"transport_above","tcp_end":[0.59578,0.17398,0.28301],"tcp_start":[0.53162,-0.02058,0.16837],"tcp_to_object_dist_end":0.0304,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.61129,0.20456,0.20895],"object_pos_start":[0.60272,0.17216,0.25346],"object_to_goal_dist_end":0.02326,"object_to_goal_dist_start":0.07258,"object_z_max":0.2552,"peak_contact_force":0.13469,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2823.0,"raw_peak_contact_force":0.453,"subtask_id":"reach_goal","tcp_end":[0.60281,0.20616,0.2395],"tcp_start":[0.59578,0.17398,0.28301],"tcp_to_object_dist_end":0.03175,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```