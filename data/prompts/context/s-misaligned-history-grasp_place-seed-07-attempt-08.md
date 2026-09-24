## Search State

- **Seed**: 7
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | 0.2263 | 0.87 | ❌ rejected |
| 7 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | 0.2924 | 1.00 | ❌ rejected |
| 6 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | 0.2932 | 1.00 | ✅ accepted |
| 5 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | 0.1669 | 0.75 | ✅ accepted |
| 4 | descend → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | -0.2118 | 0.18 | ❌ rejected |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.212) — your mutation base

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
    tolerance: 0.01
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
    tolerance: 0.02
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
  generator: arc_cartesian
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
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
    tolerance: 0.015
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.01
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.03], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_height_offset: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.212
- **task_score** (E): 0.183
- **fitness_score**: 0.458  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_approach | 1.00 | 1.00 | 0.1167 |
| descend_to_grasp | 1.00 | 1.00 | 0.1237 |
| grasp_object | 1.00 | 1.00 | 0.0127 |
| lift_object | 1.00 | 1.00 | 0.1044 |
| transport_to_goal | 0.67 | 1.00 | 0.2247 |
| descend_to_place | 1.00 | 1.00 | 0.0655 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_approach | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.014, 0.188) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 8.196 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.507, 0.014, 0.188)→(0.506, 0.021, 0.065) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 47.311 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.021, 0.065)→(0.498, 0.021, 0.056) | (0.511, 0.022, 0.026)→(0.511, 0.021, 0.025) | 0.273→0.275 | 1.00 / 26.000 | 0.214 | 0.254 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.021, 0.056)→(0.506, 0.021, 0.160) | (0.511, 0.021, 0.025)→(0.508, 0.024, 0.090) | 0.275→0.248 | 1.00 / 17.333 | 91001.595 | 0.321 |
| transport_to_goal | approach | 0.67 / step_budget | (0.506, 0.021, 0.160)→(0.591, 0.180, 0.285) | (0.508, 0.024, 0.090)→(0.503, 0.053, 0.019) | 0.248→0.260 | 1.00 / 9.000 | 0.123 | 1.016 |
| descend_to_place | descend | 1.00 / step_budget | (0.591, 0.180, 0.285)→(0.600, 0.202, 0.224) | (0.503, 0.053, 0.019)→(0.503, 0.053, 0.019) | 0.260→0.260 | 1.00 / 8.333 | 91002.826 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.255
- phase_score: 0.549
- phase_breakdown.reach_grasp_height_score: 0.751
- phase_breakdown.lift_clearance_score: 0.675
- phase_breakdown.reach_goal_score: 0.551
- phase_breakdown.transport_above_score: 0.542
- phase_breakdown.reach_approach_score: 0.223
- grasp_place_fitness: 0.579

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.579
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.255
- **Median Q (composite search score)**: -0.145
- **K-run variance**: 0.0180
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.331


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.61556,"average_solve_count":450.0,"average_success_count":450.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.12612,"descend_approach.approach_speed":0.01483,"descend_to_grasp.descend_speed":0.02812,"descend_to_grasp.grasp_height":0.02002,"descend_to_place.place_height_offset":0.01701,"descend_to_place.place_speed":0.01936,"lift_object.lift_height":0.1552,"lift_object.lift_speed":0.0272,"transport_to_goal.arc_height":0.13078,"transport_to_goal.transport_height":0.06847,"transport_to_goal.transport_speed":0.06749},"optimized_scores":{"best_composite_score":-0.09139,"best_fitness_score":0.57861,"best_task_score":0.2552},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2084.0,"contact_point_centroid":[0.5057,0.07002,-0.00245],"force_p95":0.18098,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32953,"mean_force":0.14193,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55619,0.09483,0.23284]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":412.0,"contact_point_centroid":[0.50498,0.01943,0.16051],"force_p95":0.19178,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29435,"mean_force":0.11071,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50692,0.03796,0.16549]},{"body_a":"world","body_b":"grasp_target","contact_count":111.0,"contact_point_centroid":[0.50938,0.03684,-0.00172],"force_p95":0.24752,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28468,"mean_force":0.09447,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49838,0.03644,0.05621]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51262,0.03963,-0.00222],"force_p95":0.18712,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24073,"mean_force":0.13821,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50054,0.03661,0.05647]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4474.0,"contact_point_centroid":[0.50177,0.05537,0.10185],"force_p95":0.12504,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23281,"mean_force":0.09068,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50161,0.03681,0.10569]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":585.0,"contact_point_centroid":[0.50706,0.05601,0.16298],"force_p95":0.15469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21072,"mean_force":0.08186,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50697,0.03831,0.16748]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4696.0,"contact_point_centroid":[0.50005,0.01826,0.10079],"force_p95":0.11957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20947,"mean_force":0.08578,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50149,0.0368,0.1047]},{"body_a":"world","body_b":"grasp_target","contact_count":492.0,"contact_point_centroid":[0.51251,0.03972,-0.00174],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12362,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.50246,0.00955,0.26211]},{"body_a":"world","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50624,0.03091,0.13349]},{"body_a":"world","body_b":"grasp_target","contact_count":484.0,"contact_point_centroid":[0.50567,0.07023,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61595,0.16302,0.19799]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2647.0,"contact_point_centroid":[0.49887,0.01783,0.0517],"force_p95":0.09872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12061,"mean_force":0.07597,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49942,0.03652,0.05521]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2891.0,"contact_point_centroid":[0.50021,0.05542,0.05172],"force_p95":0.10264,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10318,"mean_force":0.07261,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49943,0.03653,0.05523]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1963.0,"contact_point_centroid":[0.56205,0.10082,0.23901],"force_p95":0.01138,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01629,"mean_force":0.01054,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56158,0.10081,0.23677]},{"body_a":"left_finger","body_b":"right_finger","contact_count":513.0,"contact_point_centroid":[0.61641,0.1631,0.19991],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01052,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.616,0.16307,0.19767]}],"total_contact_groups":14},"final_pose_error":0.01464,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.50567,0.07023,0.01602],"final_tcp_position":[0.61989,0.16731,0.17336],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":30.49117,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":124.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12257,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":492.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.50741,0.02502,0.20332],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":30.49117,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1112.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_grasp_height","tcp_end":[0.50767,0.03711,0.06481],"tcp_start":[0.50741,0.02502,0.20332],"tcp_to_object_dist_end":0.03918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51252,0.03784,0.02524],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21383,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.18175,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7338.0,"raw_peak_contact_force":0.24073,"subtask_id":"reach_grasp_height","tcp_end":[0.49939,0.03652,0.05518],"tcp_start":[0.50767,0.03711,0.06481],"tcp_to_object_dist_end":0.03272,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":406.0,"n_steps_budget":1000.0,"object_pos_end":[0.51005,0.03829,0.12592],"object_pos_start":[0.51252,0.03784,0.02524],"object_to_goal_dist_end":0.17943,"object_to_goal_dist_start":0.21383,"object_z_max":0.12567,"peak_contact_force":0.14448,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9281.0,"raw_peak_contact_force":0.28468,"subtask_id":"lift_clearance","tcp_end":[0.50743,0.0374,0.16119],"tcp_start":[0.49939,0.03652,0.05518],"tcp_to_object_dist_end":0.03538,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":649.0,"n_steps_budget":1000.0,"object_pos_end":[0.50567,0.07023,0.01602],"object_pos_start":[0.51005,0.03829,0.12592],"object_to_goal_dist_end":0.20485,"object_to_goal_dist_start":0.17943,"object_z_max":0.13536,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5044.0,"raw_peak_contact_force":1.32953,"subtask_id":"transport_above","tcp_end":[0.61429,0.15971,0.22057],"tcp_start":[0.50743,0.0374,0.16119],"tcp_to_object_dist_end":0.24829,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":121.0,"n_steps_budget":1000.0,"object_pos_end":[0.50567,0.07023,0.01602],"object_pos_start":[0.50567,0.07023,0.01602],"object_to_goal_dist_end":0.20485,"object_to_goal_dist_start":0.20485,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":997.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.61989,0.16731,0.17336],"tcp_start":[0.61429,0.15971,0.22057],"tcp_to_object_dist_end":0.21732,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.87703,"average_solve_count":431.0,"average_success_count":431.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.12628,"descend_approach.approach_speed":0.06247,"descend_to_grasp.descend_speed":0.02859,"descend_to_grasp.grasp_height":0.02004,"descend_to_place.place_height_offset":0.02589,"descend_to_place.place_speed":0.01945,"lift_object.lift_height":0.16073,"lift_object.lift_speed":0.03341,"transport_to_goal.arc_height":0.12193,"transport_to_goal.transport_height":0.0671,"transport_to_goal.transport_speed":0.03517},"optimized_scores":{"best_composite_score":-0.39909,"best_fitness_score":0.27091,"best_task_score":0.14603},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1250.0,"contact_point_centroid":[0.47955,0.04916,-0.0022],"force_p95":0.27031,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40561,"mean_force":0.14065,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47397,0.04505,0.11629]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48282,0.04889,-0.00241],"force_p95":0.29315,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3096,"mean_force":0.17393,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47295,0.04505,0.05779]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":259.0,"contact_point_centroid":[0.47575,0.02847,0.05321],"force_p95":0.24313,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29481,"mean_force":0.14025,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47076,0.04481,0.05958]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":665.0,"contact_point_centroid":[0.47013,0.05949,0.05796],"force_p95":0.16989,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24134,"mean_force":0.07473,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47052,0.04478,0.06197]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2330.0,"contact_point_centroid":[0.47157,0.02662,0.05166],"force_p95":0.13912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17123,"mean_force":0.09845,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47188,0.04494,0.05667]},{"body_a":"world","body_b":"grasp_target","contact_count":412.0,"contact_point_centroid":[0.4827,0.04873,-0.0017],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12384,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.49534,0.01363,0.257]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47916,0.05299,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12296,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49612,0.08053,0.28605]},{"body_a":"world","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48317,0.03827,0.13374]},{"body_a":"world","body_b":"grasp_target","contact_count":624.0,"contact_point_centroid":[0.47916,0.05299,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56878,0.2092,0.29438]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2981.0,"contact_point_centroid":[0.47112,0.063,0.05292],"force_p95":0.10272,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11687,"mean_force":0.07222,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4719,0.04494,0.05669]},{"body_a":"left_finger","body_b":"right_finger","contact_count":818.0,"contact_point_centroid":[0.47587,0.04519,0.13889],"force_p95":0.01267,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01633,"mean_force":0.01089,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47555,0.04518,0.13677]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4219.0,"contact_point_centroid":[0.49653,0.08076,0.28839],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01291,"mean_force":0.01056,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49623,0.08074,0.28615]},{"body_a":"left_finger","body_b":"right_finger","contact_count":666.0,"contact_point_centroid":[0.56915,0.20923,0.29659],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01265,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56878,0.2092,0.29437]}],"total_contact_groups":13},"final_pose_error":0.01493,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.47916,0.05299,0.02602],"final_tcp_position":[0.57497,0.22007,0.26628],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273008.23415,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":104.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":24.3427,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":412.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.48875,0.03131,0.2023],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":30.29963,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1112.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_grasp_height","tcp_end":[0.47979,0.04562,0.06531],"tcp_start":[0.48875,0.03131,0.2023],"tcp_to_object_dist_end":0.03952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48281,0.04584,0.02336],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29362,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.31022,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7111.0,"raw_peak_contact_force":0.3096,"subtask_id":"reach_grasp_height","tcp_end":[0.47187,0.04494,0.05665],"tcp_start":[0.47979,0.04562,0.06531],"tcp_to_object_dist_end":0.03506,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.47916,0.053,0.02602],"object_pos_start":[0.48281,0.04584,0.02336],"object_to_goal_dist_end":0.28858,"object_to_goal_dist_start":0.29362,"object_z_max":0.0346,"peak_contact_force":273004.49675,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2992.0,"raw_peak_contact_force":0.40561,"subtask_id":"lift_clearance","tcp_end":[0.47815,0.0454,0.16491],"tcp_start":[0.47187,0.04494,0.05665],"tcp_to_object_dist_end":0.1391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47916,0.05299,0.02602],"object_pos_start":[0.47916,0.053,0.02602],"object_to_goal_dist_end":0.28859,"object_to_goal_dist_start":0.28858,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8219.0,"raw_peak_contact_force":0.12296,"subtask_id":"transport_above","tcp_end":[0.56472,0.20041,0.32114],"tcp_start":[0.47815,0.0454,0.16491],"tcp_to_object_dist_end":0.34081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":156.0,"n_steps_budget":1000.0,"object_pos_end":[0.47916,0.05299,0.02602],"object_pos_start":[0.47916,0.05299,0.02602],"object_to_goal_dist_end":0.28859,"object_to_goal_dist_start":0.28859,"object_z_max":0.02602,"peak_contact_force":273008.23415,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1290.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.57497,0.22007,0.26628],"tcp_start":[0.56472,0.20041,0.32114],"tcp_to_object_dist_end":0.30793,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.78815,"average_solve_count":439.0,"average_success_count":439.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_approach.approach_height":0.08083,"descend_approach.approach_speed":0.07703,"descend_to_grasp.descend_speed":0.02008,"descend_to_grasp.grasp_height":0.02047,"descend_to_place.place_height_offset":0.01518,"descend_to_place.place_speed":0.02017,"lift_object.lift_height":0.1462,"lift_object.lift_speed":0.04067,"transport_to_goal.arc_height":0.09378,"transport_to_goal.transport_height":0.09072,"transport_to_goal.transport_speed":0.015},"optimized_scores":{"best_composite_score":-0.14485,"best_fitness_score":0.52515,"best_task_score":0.14924},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3173.0,"contact_point_centroid":[0.52406,0.03414,-0.00226],"force_p95":0.13031,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.59674,"mean_force":0.13961,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5565,0.06499,0.28486]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":822.0,"contact_point_centroid":[0.53146,-0.03832,0.15957],"force_p95":0.18681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32152,"mean_force":0.12013,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52966,-0.01992,0.16459]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1283.0,"contact_point_centroid":[0.53019,-0.00226,0.16346],"force_p95":0.15639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28253,"mean_force":0.09031,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5295,-0.01963,0.16795]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3907.0,"contact_point_centroid":[0.52613,-0.03851,0.09729],"force_p95":0.14175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27166,"mean_force":0.10059,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52487,-0.02006,0.10102]},{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.53432,-0.01999,-0.00152],"force_p95":0.24899,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26288,"mean_force":0.08458,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52094,-0.01975,0.05585]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4204.0,"contact_point_centroid":[0.52503,-0.00188,0.09751],"force_p95":0.128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22636,"mean_force":0.08932,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5249,-0.02006,0.10096]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53708,-0.02131,-0.00212],"force_p95":0.15608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21081,"mean_force":0.1319,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52301,-0.01978,0.05619]},{"body_a":"world","body_b":"grasp_target","contact_count":552.0,"contact_point_centroid":[0.53702,-0.02132,-0.00177],"force_p95":0.13794,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12351,"phase_index":0.0,"phase_name":"descend_approach","phase_type":"descend","tcp_position_centroid":[0.51236,-0.00688,0.23494]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2827.0,"contact_point_centroid":[0.5232,-0.03853,0.0517],"force_p95":0.11886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1249,"mean_force":0.07803,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52186,-0.01976,0.05483]},{"body_a":"world","body_b":"grasp_target","contact_count":772.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52626,-0.01738,0.11181]},{"body_a":"world","body_b":"grasp_target","contact_count":912.0,"contact_point_centroid":[0.52413,0.03448,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59827,0.1979,0.27235]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2973.0,"contact_point_centroid":[0.52265,-0.00121,0.05158],"force_p95":0.09337,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11131,"mean_force":0.06795,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52185,-0.01976,0.05482]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3193.0,"contact_point_centroid":[0.55836,0.06942,0.29144],"force_p95":0.0112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01562,"mean_force":0.01055,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55797,0.06942,0.28909]},{"body_a":"left_finger","body_b":"right_finger","contact_count":972.0,"contact_point_centroid":[0.5987,0.19791,0.27454],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59827,0.1979,0.27235]}],"total_contact_groups":14},"final_pose_error":0.01467,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.52413,0.03448,0.01602],"final_tcp_position":[0.60447,0.21756,0.23137],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":139.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":552.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_approach","tcp_end":[0.52597,-0.01514,0.15898],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":772.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_grasp_height","tcp_end":[0.53039,-0.01987,0.06525],"tcp_start":[0.52597,-0.01514,0.15898],"tcp_to_object_dist_end":0.03982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53722,-0.02061,0.02553],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3164,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.15107,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7600.0,"raw_peak_contact_force":0.21081,"subtask_id":"reach_grasp_height","tcp_end":[0.52182,-0.01976,0.05479],"tcp_start":[0.53039,-0.01987,0.06525],"tcp_to_object_dist_end":0.03307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.53579,-0.0207,0.11737],"object_pos_start":[0.53722,-0.02061,0.02553],"object_to_goal_dist_end":0.27458,"object_to_goal_dist_start":0.3164,"object_z_max":0.11713,"peak_contact_force":0.14289,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8209.0,"raw_peak_contact_force":0.27166,"subtask_id":"lift_clearance","tcp_end":[0.53166,-0.02043,0.1526],"tcp_start":[0.52182,-0.01976,0.05479],"tcp_to_object_dist_end":0.03547,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52413,0.03448,0.01602],"object_pos_start":[0.53579,-0.0207,0.11737],"object_to_goal_dist_end":0.28533,"object_to_goal_dist_start":0.27458,"object_z_max":0.14225,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8471.0,"raw_peak_contact_force":1.59674,"subtask_id":"transport_above","tcp_end":[0.59415,0.18125,0.31233],"tcp_start":[0.53166,-0.02043,0.1526],"tcp_to_object_dist_end":0.338,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.52413,0.03448,0.01602],"object_pos_start":[0.52413,0.03448,0.01602],"object_to_goal_dist_end":0.28533,"object_to_goal_dist_start":0.28533,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1884.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.60447,0.21756,0.23137],"tcp_start":[0.59415,0.18125,0.31233],"tcp_to_object_dist_end":0.29385,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```